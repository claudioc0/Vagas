package provider

import (
	"context"
	"encoding/json"
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
		},
	}
}

func (p *RemotarProvider) ID() string   { return "remotar" }
func (p *RemotarProvider) Name() string { return "Remotar (Vagas 100% Remotas)" }

func (p *RemotarProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	var mu sync.Mutex
	var allJobs []domain.Job
	var wg sync.WaitGroup

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
			if err != nil {
				return
			}

			mu.Lock()
			allJobs = append(allJobs, jobs...)
			mu.Unlock()
		}(q)
	}

	wg.Wait()
	return allJobs, nil
}

func (p *RemotarProvider) fetchQuery(ctx context.Context, query string) ([]domain.Job, error) {
	apiURL := fmt.Sprintf("https://api.remotar.com.br/jobs?search=%s&limit=20&page=1", url.QueryEscape(query))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, apiURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VagasHunter/1.0")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("remotar api status %d", resp.StatusCode)
	}

	var res RemotarResponse
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, err
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

	return jobs, nil
}
