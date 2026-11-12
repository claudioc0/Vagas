package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"sync"
	"time"
	"vagas-go/internal/domain"
)

type GitHubIssue struct {
	Title       string    `json:"title"`
	HTMLURL     string    `json:"html_url"`
	Body        string    `json:"body"`
	CreatedAt   time.Time `json:"created_at"`
	PullRequest any       `json:"pull_request,omitempty"`
	Labels      []struct {
		Name string `json:"name"`
	} `json:"labels"`
}

type GitHubProvider struct {
	client *http.Client
	repos  []string
}

func NewGitHubProvider() *GitHubProvider {
	return &GitHubProvider{
		client: &http.Client{Timeout: 10 * time.Second},
		repos: []string{
			"backend-br/vagas",
			"frontendbr/vagas",
			"react-brasil/vagas",
			"qa-brasil/vagas",
			"soujava/vagas-java",
			"androiddevbr/vagas",
			"flutterbr/vagas",
			"phpdevbr/vagas",
			"vuejs-br/vagas",
			"datascience-br/vagas",
			"DevOps-Brasil/Vagas",
		},
	}
}

func (p *GitHubProvider) ID() string   { return "github_issues" }
func (p *GitHubProvider) Name() string { return "GitHub Issues (11 Repos Tech Brasil)" }

func (p *GitHubProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	var mu sync.Mutex
	var allJobs []domain.Job
	var wg sync.WaitGroup

	limitChan := make(chan struct{}, 4) // Até 4 repositórios em paralelo
	maxAge := 30 * 24 * time.Hour

	for _, repo := range p.repos {
		wg.Add(1)
		go func(r string) {
			defer wg.Done()
			select {
			case limitChan <- struct{}{}:
				defer func() { <-limitChan }()
			case <-ctx.Done():
				return
			}

			jobs, err := p.fetchRepo(ctx, r, maxAge)
			if err != nil {
				return
			}

			mu.Lock()
			allJobs = append(allJobs, jobs...)
			mu.Unlock()
		}(repo)
	}

	wg.Wait()
	return allJobs, nil
}

func (p *GitHubProvider) fetchRepo(ctx context.Context, repo string, maxAge time.Duration) ([]domain.Job, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/issues?state=open&per_page=30", repo)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "VagasGo-Hunter/1.0")
	req.Header.Set("Accept", "application/vnd.github.v3+json")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("github api status %d", resp.StatusCode)
	}

	var issues []GitHubIssue
	if err := json.NewDecoder(resp.Body).Decode(&issues); err != nil {
		return nil, err
	}

	repoOwner := strings.Split(repo, "/")[0]
	now := time.Now()
	var jobs []domain.Job

	for _, iss := range issues {
		if iss.PullRequest != nil {
			continue
		}
		if now.Sub(iss.CreatedAt) > maxAge {
			continue
		}

		// Extrair modalidade
		mod := domain.ModalityUnknown
		lowerText := strings.ToLower(iss.Title + " " + iss.Body)
		if strings.Contains(lowerText, "remoto") || strings.Contains(lowerText, "remote") {
			mod = domain.ModalityRemote
		} else if strings.Contains(lowerText, "híbrido") || strings.Contains(lowerText, "hibrido") {
			mod = domain.ModalityHybrid
		} else if strings.Contains(lowerText, "presencial") {
			mod = domain.ModalityOnSite
		}

		desc := iss.Body
		if len(desc) > 500 {
			desc = desc[:500] + "..."
		}

		job := domain.Job{
			SourceID:    p.ID(),
			Title:       strings.TrimSpace(iss.Title),
			Company:     repoOwner,
			Location:    "Brasil",
			Modality:    mod,
			Seniority:   "Júnior / Tech",
			URL:         iss.HTMLURL,
			Description: desc,
			PublishedAt: iss.CreatedAt,
			CollectedAt: now,
		}
		job.ID = job.GenerateID()
		jobs = append(jobs, job)
	}

	return jobs, nil
}
