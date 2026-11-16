package provider

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
	"vagas-go/internal/domain"
)

type RemotarItem struct {
	ID                 any    `json:"id"`
	Title              string `json:"title"`
	CompanyDisplayName string `json:"companyDisplayName"`
	Company            struct {
		Name string `json:"name"`
	} `json:"company"`
	ExternalLink string `json:"externalLink"`
	Description  string `json:"description"`
	CreatedAt    string `json:"createdAt"`
}

type RemotarResponse struct {
	Data []RemotarItem `json:"data"`
}

type RemotarProvider struct {
	client  *http.Client
	queries []string
}

func NewRemotarProvider() *RemotarProvider {
	return &RemotarProvider{
		client: &http.Client{Timeout: 10 * time.Second},
		queries: []string{
			"desenvolvedor junior",
			"junior",
			"trainee tecnologia",
			"python junior",
			"full stack junior",
			"front end junior",
			"back end junior",
			"inteligencia artificial",
			"dados junior",
			"analista de sistemas junior",
			"qa junior",
			"devops junior",
			"seguranca da informacao junior",
			"desenvolvedor mobile junior",
			"javascript junior",
			"react junior",
			"node junior",
			"java junior",
			"trainee ti",
			"engenheiro de dados junior",
		},
	}
}

func (p *RemotarProvider) ID() string   { return "remotar" }
func (p *RemotarProvider) Name() string { return "Remotar (Vagas 100% Remotas)" }

func (p *RemotarProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	var mu sync.Mutex
	var allJobs []domain.Job
	var wg sync.WaitGroup
	var errs []error

	limit := make(chan struct{}, 3)

	for _, q := range p.queries {
		wg.Add(1)
		go func(query string) {
			defer wg.Done()
			select {
			case limit <- struct{}{}:
				defer func() { <-limit }()
			case <-ctx.Done():
				return
			}

			jobs, err := p.fetchQuery(ctx, query)

			mu.Lock()
			allJobs = append(allJobs, jobs...)
			if err != nil {
				errs = append(errs, fmt.Errorf("busca %q: %w", query, err))
			}
			mu.Unlock()
		}(q)
	}

	wg.Wait()
	// Resultado parcial é válido: devolve o coletado junto com os erros
	return allJobs, errors.Join(errs...)
}

const (
	remotarPageSize = 20
	remotarMaxPages = 3
)

// fetchQuery pagina uma busca (até remotarMaxPages páginas); em erro devolve o já coletado.
func (p *RemotarProvider) fetchQuery(ctx context.Context, query string) ([]domain.Job, error) {
	var all []domain.Job
	for page := 1; page <= remotarMaxPages; page++ {
		jobs, n, err := p.fetchPage(ctx, query, page)
		all = append(all, jobs...)
		if err != nil {
			return all, fmt.Errorf("página %d: %w", page, err)
		}
		if n < remotarPageSize {
			break
		}
	}
	return all, nil
}

// fetchPage retorna as vagas da página e o total bruto de itens recebidos.
func (p *RemotarProvider) fetchPage(ctx context.Context, query string, page int) ([]domain.Job, int, error) {
	apiURL := fmt.Sprintf("https://api.remotar.com.br/jobs?search=%s&limit=%d&page=%d", url.QueryEscape(query), remotarPageSize, page)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, apiURL, nil)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VagasHunter/1.0")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, 0, fmt.Errorf("remotar api status %d", resp.StatusCode)
	}

	var res RemotarResponse
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, 0, err
	}

	var jobs []domain.Job
	now := time.Now()

	for _, item := range res.Data {
		company := item.CompanyDisplayName
		if company == "" {
			company = item.Company.Name
		}
		if company == "" {
			company = "Confidencial / Remotar"
		}

		link := item.ExternalLink
		if link == "" {
			link = fmt.Sprintf("https://remotar.com.br/job/%v", item.ID)
		}

		desc := item.Description
		if len(desc) > 500 {
			desc = desc[:500] + "..."
		}

		parsedDate, _ := time.Parse(time.RFC3339, item.CreatedAt)
		if parsedDate.IsZero() {
			parsedDate = now
		}

		job := domain.Job{
			SourceID:    p.ID(),
			Title:       strings.TrimSpace(item.Title),
			Company:     strings.TrimSpace(company),
			Location:    "Brasil (100% Remoto)",
			Modality:    domain.ModalityRemote,
			Seniority:   "Júnior",
			URL:         link,
			Description: desc,
			PublishedAt: parsedDate,
			CollectedAt: now,
		}
		job.ID = job.GenerateID()
		jobs = append(jobs, job)
	}

	return jobs, len(res.Data), nil
}
