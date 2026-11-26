package provider

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"net/http"
	"net/url"
	"strings"
	"time"
	"vagas-go/internal/domain"
)

// Freelancer.com: API pública de projetos ativos (não exige chave).
// Os cortes de concorrência, orçamento, idioma e idade ficam aqui; a relevância
// da área é avaliada por fitscore.Evaluate.
const (
	freelancerMinFixedUSD  = 100.0
	freelancerMinHourlyUSD = 15.0
)

type FreelancerProvider struct {
	freelanceSource
	client  *http.Client
	queries []string
}

func NewFreelancerProvider() *FreelancerProvider {
	return &FreelancerProvider{
		client: &http.Client{Timeout: 15 * time.Second},
		queries: []string{
			"ai agent", "chatbot", "llm", "openai", "automation", "python",
			"golang", "react", "node.js", "data analysis", "web scraping", "api integration",
		},
	}
}

func (p *FreelancerProvider) ID() string   { return "freelancer" }
func (p *FreelancerProvider) Name() string { return "Freelancer.com (Projetos)" }

type freelancerProject struct {
	Title       string `json:"title"`
	SEOURL      string `json:"seo_url"`
	Description string `json:"description"`
	Type        string `json:"type"` // "fixed" ou "hourly"
	Status      string `json:"status"`
	Language    string `json:"language"`
	Submitted   int64  `json:"time_submitted"`
	Budget      struct {
		Minimum float64 `json:"minimum"`
		Maximum float64 `json:"maximum"`
	} `json:"budget"`
	Currency struct {
		Code         string  `json:"code"`
		ExchangeRate float64 `json:"exchange_rate"` // valor de 1 unidade em USD
	} `json:"currency"`
	BidStats struct {
		BidCount int `json:"bid_count"`
	} `json:"bid_stats"`
	Skills []struct {
		Name string `json:"name"`
	} `json:"jobs"`
}

func (p *FreelancerProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	var (
		all  []domain.Job
		errs []error
		seen = make(map[string]bool)
	)
	now := time.Now()
	for _, q := range p.queries {
		projects, err := p.fetchQuery(ctx, q)
		if err != nil {
			errs = append(errs, fmt.Errorf("busca %q: %w", q, err))
			continue
		}
		for _, pr := range projects {
			if seen[pr.SEOURL] || !pr.accepted(now) {
				continue
			}
			seen[pr.SEOURL] = true
			all = append(all, pr.toJob(p.ID(), now))
		}
	}
	return all, errors.Join(errs...)
}

func (p *FreelancerProvider) fetchQuery(ctx context.Context, query string) ([]freelancerProject, error) {
	params := url.Values{
		"query":            {query},
		"limit":            {"100"},
		"full_description": {"true"},
		"job_details":      {"true"},
		"sort_field":       {"time_submitted"},
		"languages[]":      {"en", "pt"},
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet,
		"https://www.freelancer.com/api/projects/0.1/projects/active/?"+params.Encode(), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "VagasHunter/1.0")

	resp, err := p.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("freelancer status %d", resp.StatusCode)
	}

	var payload struct {
		Status string `json:"status"`
		Result struct {
			Projects []freelancerProject `json:"projects"`
		} `json:"result"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
		return nil, err
	}
	if payload.Status != "success" {
		return nil, fmt.Errorf("freelancer respondeu %q", payload.Status)
	}
	return payload.Result.Projects, nil
}

// accepted aplica os cortes: aberto, en/pt, recente, poucas propostas e orçamento mínimo.
// O orçamento comparado é o meio da faixa (ou o piso, quando não há teto), em USD.
func (pr freelancerProject) accepted(now time.Time) bool {
	if pr.SEOURL == "" || pr.Status != "active" {
		return false
	}
	if pr.Language != "en" && pr.Language != "pt" {
		return false
	}
	if now.Sub(time.Unix(pr.Submitted, 0)) > freelanceMaxAge {
		return false
	}
	if pr.BidStats.BidCount > freelanceMaxBids {
		return false
	}
	mid := (pr.Budget.Minimum + math.Max(pr.Budget.Minimum, pr.Budget.Maximum)) / 2 * pr.Currency.ExchangeRate
	if pr.Type == "hourly" {
		return mid >= freelancerMinHourlyUSD
	}
	return mid >= freelancerMinFixedUSD
}

func (pr freelancerProject) budgetText() string {
	amount := fmt.Sprintf("%.0f", pr.Budget.Minimum)
	if pr.Budget.Maximum > pr.Budget.Minimum {
		amount += fmt.Sprintf("–%.0f", pr.Budget.Maximum)
	}
	kind := "fixo"
	if pr.Type == "hourly" {
		kind = "por hora"
	}
	return fmt.Sprintf("%s %s (%s)", pr.Currency.Code, amount, kind)
}

func (pr freelancerProject) toJob(source string, now time.Time) domain.Job {
	skills := make([]string, 0, len(pr.Skills))
	for _, s := range pr.Skills {
		skills = append(skills, s.Name)
	}
	job := domain.Job{
		SourceID: source,
		Title:    strings.TrimSpace(pr.Title),
		Company:  "Freelancer.com",
		// Para projetos, a localização guarda orçamento e concorrência
		Location:    fmt.Sprintf("%s · %d propostas", pr.budgetText(), pr.BidStats.BidCount),
		Modality:    domain.ModalityRemote,
		Seniority:   domain.SeniorityFreelance,
		URL:         "https://www.freelancer.com/projects/" + pr.SEOURL,
		Description: truncateDesc("Skills: " + strings.Join(skills, ", ") + "\n" + pr.Description),
		Skills:      skills,
		Bids:        pr.BidStats.BidCount,
		PublishedAt: time.Unix(pr.Submitted, 0),
		CollectedAt: now,
	}
	job.ID = job.GenerateID()
	return job
}
