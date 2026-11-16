package provider

import (
	"context"
	"errors"
	"fmt"
	"html"
	"io"
	"net/http"
	"regexp"
	"strings"
	"sync"
	"time"
	"vagas-go/internal/domain"
)

// Catho: as páginas de busca (/vagas/<termo>/[<cidade-uf>/]) são renderizadas no servidor.
// O robots.txt permite o acesso. A listagem não traz descrição, então o scorer avalia
// apenas o título (que precisa conter "júnior"/"jr"/"trainee" para virar Nível A).

var (
	reCathoDate    = regexp.MustCompile(`(\d{1,2})/(\d{1,2})`)
	reCathoTitle   = regexp.MustCompile(`title="([^"]*)"\s+data-navigation-offer`)
	reCathoHref    = regexp.MustCompile(`href="(/vagas/[^"]+/\d+)"`)
	reCathoTag     = regexp.MustCompile(`(?s)<span class="tag pub_[^"]*"[^>]*>(.*?)</span>`)
	reCathoCompany = regexp.MustCompile(`(?s)<p class="mb-2">\s*<span class="text-12">(.*?)</span>`)
	reCathoLoc     = regexp.MustCompile(`(?s)i_job_location"></span>(.*?)</p>`)
	reHTMLTag      = regexp.MustCompile(`<[^>]+>`)
	reCathoRemote  = regexp.MustCompile(`(?i)(trabalhe\s+de\s+casa|work\s+from\s+home|home\s*office|remot[oa]|100%\s*remot)`)
)

type CathoProvider struct {
	client *http.Client
	terms  []string
	cities []string // "" = busca nacional
}

func NewCathoProvider() *CathoProvider {
	return &CathoProvider{
		client: &http.Client{Timeout: 15 * time.Second},
		terms: []string{
			"desenvolvedor-junior",
			"programador-junior",
			"analista-de-sistemas-junior",
			"analista-desenvolvedor-junior",
			"engenheiro-de-software-junior",
			"full-stack-junior",
			"front-end-junior",
			"back-end-junior",
			"python-junior",
			"java-junior",
			"analista-de-dados-junior",
			"qa-junior",
			"devops-junior",
			"trainee-ti",
		},
		cities: []string{"", "curitiba-pr"},
	}
}

func (p *CathoProvider) ID() string   { return "catho" }
func (p *CathoProvider) Name() string { return "Catho (Vagas)" }

const (
	cathoPageSize = 20
	cathoMaxPages = 3
	cathoMaxAge   = 30 * 24 * time.Hour
)

func (p *CathoProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	var (
		mu      sync.Mutex
		wg      sync.WaitGroup
		allJobs []domain.Job
		errs    []error
		limit   = make(chan struct{}, 3)
	)

	for _, term := range p.terms {
		for _, city := range p.cities {
			path := term + "/"
			if city != "" {
				path += city + "/"
			}
			wg.Add(1)
			go func(path string) {
				defer wg.Done()
				select {
				case limit <- struct{}{}:
					defer func() { <-limit }()
				case <-ctx.Done():
					return
				}

				jobs, err := p.fetchSearch(ctx, path)

				mu.Lock()
				allJobs = append(allJobs, jobs...)
				if err != nil {
					errs = append(errs, fmt.Errorf("busca %q: %w", path, err))
				}
				mu.Unlock()
			}(path)
		}
	}

	wg.Wait()
	return allJobs, errors.Join(errs...)
}

func (p *CathoProvider) fetchSearch(ctx context.Context, path string) ([]domain.Job, error) {
	var all []domain.Job
	for page := 1; page <= cathoMaxPages; page++ {
		u := "https://www.catho.com.br/vagas/" + path
		if page > 1 {
			u += fmt.Sprintf("?page=%d", page)
		}
		jobs, n, err := p.fetchPage(ctx, u)
		all = append(all, jobs...)
		if err != nil {
			return all, fmt.Errorf("página %d: %w", page, err)
		}
		if n < cathoPageSize {
			break
		}
	}
	return all, nil
}

// fetchPage devolve as vagas recentes e o total bruto de cartões na página.
func (p *CathoProvider) fetchPage(ctx context.Context, pageURL string) ([]domain.Job, int, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, pageURL, nil)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VagasHunter/1.0")
	req.Header.Set("Accept", "text/html")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()

	// 404 = termo/cidade sem resultados na Catho; não é falha
	if resp.StatusCode == http.StatusNotFound {
		return nil, 0, nil
	}
	if resp.StatusCode != http.StatusOK {
		return nil, 0, fmt.Errorf("catho status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(io.LimitReader(resp.Body, 8<<20))
	if err != nil {
		return nil, 0, err
	}

	cards := strings.Split(string(body), `<li data-offer-item="`)[1:]
	// Se o layout mudar, a fonte inteira volta com 0 vagas e o engine avisa no Telegram

	now := time.Now()
	var jobs []domain.Job
	for _, card := range cards {
		titleM := reCathoTitle.FindStringSubmatch(card)
		hrefM := reCathoHref.FindStringSubmatch(card)
		if titleM == nil || hrefM == nil {
			continue
		}
		title := cleanText(titleM[1])

		published := now
		if tm := reCathoTag.FindStringSubmatch(card); tm != nil {
			published = parseCathoDate(cleanText(tm[1]), now)
		}
		if now.Sub(published) > cathoMaxAge {
			continue
		}

		company := ""
		if m := reCathoCompany.FindStringSubmatch(card); m != nil {
			company = cleanText(m[1])
		}
		if company == "" || strings.Trim(company, "*") == "" {
			company = "Confidencial / Catho"
		}

		city := ""
		if m := reCathoLoc.FindStringSubmatch(card); m != nil {
			city = cathoCity(cleanText(m[1]))
		}
		if city == "" {
			city = "Brasil"
		}

		// Sem campo de modalidade: infere remoto pelo título/URL; o resto vale como
		// presencial para que o filtro de localização (Curitiba/PR) seja aplicado.
		mod := domain.ModalityOnSite
		if reCathoRemote.MatchString(title) || reCathoRemote.MatchString(strings.ReplaceAll(hrefM[1], "-", " ")) {
			mod = domain.ModalityRemote
		}

		job := domain.Job{
			SourceID:    p.ID(),
			Title:       title,
			Company:     company,
			Location:    city,
			Modality:    mod,
			Seniority:   "Júnior",
			URL:         "https://www.catho.com.br" + hrefM[1],
			PublishedAt: published,
			CollectedAt: now,
		}
		job.ID = job.GenerateID()
		jobs = append(jobs, job)
	}

	return jobs, len(cards), nil
}

func cleanText(s string) string {
	s = reHTMLTag.ReplaceAllString(s, " ")
	s = html.UnescapeString(s)
	return strings.Join(strings.Fields(s), " ")
}

// cathoCity extrai a cidade de textos como "1 vaga - Curitiba" ou "36 vagas - Barueri + 35 cidades".
func cathoCity(s string) string {
	if i := strings.Index(s, " - "); i >= 0 {
		s = s[i+3:]
	}
	if i := strings.Index(s, " + "); i >= 0 {
		s = s[:i]
	}
	return strings.TrimSpace(s)
}

// parseCathoDate lê "Publicada em 11/11" (sem ano); datas futuras pertencem ao ano anterior.
func parseCathoDate(s string, now time.Time) time.Time {
	m := reCathoDate.FindStringSubmatch(s)
	if m == nil {
		return now
	}
	var day, month int
	fmt.Sscanf(m[1], "%d", &day)
	fmt.Sscanf(m[2], "%d", &month)
	if day < 1 || day > 31 || month < 1 || month > 12 {
		return now
	}
	t := time.Date(now.Year(), time.Month(month), day, 12, 0, 0, 0, now.Location())
	if t.After(now.Add(48 * time.Hour)) {
		t = t.AddDate(-1, 0, 0)
	}
	return t
}
