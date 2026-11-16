package provider

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"sync"
	"time"
	"vagas-go/internal/domain"
)

// A API pública antiga da Gupy foi desativada (09/11/2026). O portal renderiza a busca
// no servidor (Next.js) e embute a lista em <script id="__NEXT_DATA__">; é isso que lemos.
// Se a Gupy mudar o formato, o provider falha de forma explícita (vira aviso no Telegram).

var reNextData = regexp.MustCompile(`(?s)<script id="__NEXT_DATA__"[^>]*>(.*?)</script>`)

type gupyJob struct {
	ID            int64     `json:"id"`
	Name          string    `json:"name"`
	Description   string    `json:"description"`
	CareerPage    string    `json:"careerPageName"`
	PublishedDate time.Time `json:"publishedDate"`
	WorkplaceType string    `json:"workplaceType"`
	City          string    `json:"city"`
	State         string    `json:"state"`
	JobURL        string    `json:"jobUrl"`
}

type gupyNextData struct {
	Props struct {
		PageProps struct {
			InitialJobList *struct {
				Data       []gupyJob `json:"data"`
				Pagination struct {
					Total  int `json:"total"`
					Limit  int `json:"limit"`
					Offset int `json:"offset"`
				} `json:"pagination"`
			} `json:"initialJobList"`
		} `json:"pageProps"`
	} `json:"props"`
}

type GupyProvider struct {
	client *http.Client
	terms  []string
	// Estados adicionais pesquisados (além da busca nacional/remota)
	states []string
}

func NewGupyProvider() *GupyProvider {
	return &GupyProvider{
		client: &http.Client{Timeout: 15 * time.Second},
		terms: []string{
			"desenvolvedor junior",
			"desenvolvedor júnior",
			"programador junior",
			"analista de sistemas junior",
			"analista desenvolvedor junior",
			"engenheiro de software junior",
			"desenvolvedor full stack junior",
			"desenvolvedor front end junior",
			"desenvolvedor back end junior",
			"desenvolvedor python junior",
			"desenvolvedor java junior",
			"analista de dados junior",
			"trainee tecnologia",
			"inteligencia artificial junior",
			"analista de suporte de sistemas junior",
			"analista de qualidade de software junior",
			"qa junior",
			"devops junior",
			"seguranca da informacao junior",
			"desenvolvedor mobile junior",
			"desenvolvedor javascript junior",
			"desenvolvedor react junior",
			"desenvolvedor node junior",
			"trainee ti",
			"cientista de dados junior",
			"engenheiro de dados junior",
		},
		states: []string{"Paraná"},
	}
}

func (p *GupyProvider) ID() string   { return "gupy" }
func (p *GupyProvider) Name() string { return "Gupy (Portal de Vagas)" }

const (
	gupyMaxPages = 3
	gupyMaxAge   = 30 * 24 * time.Hour
)

func (p *GupyProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	// Cada termo é buscado sem filtro (cobre remotas) e, adicionalmente, por estado
	var searches []string
	for _, t := range p.terms {
		base := "term=" + url.PathEscape(t)
		searches = append(searches, base)
		for _, st := range p.states {
			searches = append(searches, base+"&state="+url.PathEscape(st))
		}
	}

	var (
		mu      sync.Mutex
		wg      sync.WaitGroup
		allJobs []domain.Job
		errs    []error
		limit   = make(chan struct{}, 3)
	)

	for _, s := range searches {
		wg.Add(1)
		go func(search string) {
			defer wg.Done()
			select {
			case limit <- struct{}{}:
				defer func() { <-limit }()
			case <-ctx.Done():
				return
			}

			jobs, err := p.fetchSearch(ctx, search)

			mu.Lock()
			allJobs = append(allJobs, jobs...)
			if err != nil {
				errs = append(errs, fmt.Errorf("busca %q: %w", search, err))
			}
			mu.Unlock()
		}(s)
	}

	wg.Wait()
	return allJobs, errors.Join(errs...)
}

func (p *GupyProvider) fetchSearch(ctx context.Context, search string) ([]domain.Job, error) {
	var all []domain.Job
	for page := 1; page <= gupyMaxPages; page++ {
		q := search + "&sortBy=publishedDate"
		if page > 1 {
			q += fmt.Sprintf("&page=%d", page)
		}
		jobs, pageLimit, n, err := p.fetchPage(ctx, q)
		all = append(all, jobs...)
		if err != nil {
			return all, fmt.Errorf("página %d: %w", page, err)
		}
		if n == 0 || n < pageLimit {
			break
		}
	}
	return all, nil
}

// fetchPage devolve as vagas recentes da página, o tamanho de página informado e o total bruto recebido.
func (p *GupyProvider) fetchPage(ctx context.Context, query string) ([]domain.Job, int, int, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "https://portal.gupy.io/job-search/"+query, nil)
	if err != nil {
		return nil, 0, 0, err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VagasHunter/1.0")
	req.Header.Set("Accept", "text/html")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, 0, 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, 0, 0, fmt.Errorf("gupy status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(io.LimitReader(resp.Body, 8<<20))
	if err != nil {
		return nil, 0, 0, err
	}

	m := reNextData.FindSubmatch(body)
	if m == nil {
		return nil, 0, 0, errors.New("formato da página mudou: __NEXT_DATA__ não encontrado")
	}
	var nd gupyNextData
	if err := json.Unmarshal(m[1], &nd); err != nil {
		return nil, 0, 0, fmt.Errorf("json inválido: %w", err)
	}
	list := nd.Props.PageProps.InitialJobList
	if list == nil {
		return nil, 0, 0, errors.New("formato da página mudou: initialJobList ausente")
	}

	now := time.Now()
	var jobs []domain.Job
	for _, g := range list.Data {
		if g.PublishedDate.IsZero() || now.Sub(g.PublishedDate) > gupyMaxAge {
			continue
		}

		mod := domain.ModalityUnknown
		switch g.WorkplaceType {
		case "remote":
			mod = domain.ModalityRemote
		case "hybrid":
			mod = domain.ModalityHybrid
		case "on-site":
			mod = domain.ModalityOnSite
		}

		loc := strings.TrimSpace(strings.Trim(g.City+", "+g.State, ", "))
		if loc == "" {
			loc = "Brasil"
		}

		desc := g.Description
		desc = truncateDesc(desc)

		company := strings.TrimSpace(g.CareerPage)
		if company == "" {
			company = "Confidencial / Gupy"
		}

		job := domain.Job{
			SourceID:    p.ID(),
			Title:       strings.TrimSpace(g.Name),
			Company:     company,
			Location:    loc,
			Modality:    mod,
			Seniority:   "Júnior",
			URL:         g.JobURL,
			Description: desc,
			PublishedAt: g.PublishedDate,
			CollectedAt: now,
		}
		job.ID = job.GenerateID()
		jobs = append(jobs, job)
	}

	return jobs, list.Pagination.Limit, len(list.Data), nil
}
