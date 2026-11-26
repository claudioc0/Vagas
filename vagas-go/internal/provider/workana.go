package provider

import (
	"context"
	"encoding/json"
	"errors"
	"html"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"
	"vagas-go/internal/domain"
)

// Workana: a página de busca traz os projetos em JSON no atributo :results-initials.
// O robots.txt pede 30s entre acessos e proíbe /api/, por isso é feita uma única
// requisição à página pública por execução.
const workanaURL = "https://www.workana.com/jobs?category=it-programming&language=pt"

var (
	reWorkanaData      = regexp.MustCompile(`(?s):results-initials='(.*?)'`)
	reWorkanaTitle     = regexp.MustCompile(`<span title="([^"]*)"`)
	reWorkanaNumber    = regexp.MustCompile(`\d[\d.]*`)
	reWorkanaAgeAmount = regexp.MustCompile(`(\d+)\s*(minuto|hora)`)
)

type WorkanaProvider struct {
	freelanceSource
	client *http.Client
}

func NewWorkanaProvider() *WorkanaProvider {
	return &WorkanaProvider{client: &http.Client{Timeout: 15 * time.Second}}
}

func (p *WorkanaProvider) ID() string   { return "workana" }
func (p *WorkanaProvider) Name() string { return "Workana (Projetos)" }

func (p *WorkanaProvider) Fetch(ctx context.Context) ([]domain.Job, error) {
	body, err := fetchHTML(ctx, p.client, workanaURL)
	if err != nil {
		return nil, err
	}
	return parseWorkana(body, time.Now())
}

type workanaProject struct {
	Slug        string `json:"slug"`
	Title       string `json:"title"`
	Description string `json:"description"`
	Published   string `json:"postedDate"`
	Budget      string `json:"budget"`
	IsHourly    bool   `json:"isHourly"`
	TotalBids   string `json:"totalBids"`
	Verified    bool   `json:"hasVerifiedPaymentMethod"`
	Skills      []struct {
		Name string `json:"anchorText"`
	} `json:"skills"`
}

func parseWorkana(body string, now time.Time) ([]domain.Job, error) {
	m := reWorkanaData.FindStringSubmatch(body)
	if m == nil {
		return nil, errors.New("dados não encontrados na página (o layout pode ter mudado)")
	}
	var data struct {
		Results []workanaProject `json:"results"`
	}
	if err := json.Unmarshal([]byte(html.UnescapeString(m[1])), &data); err != nil {
		return nil, err
	}
	if len(data.Results) == 0 {
		return nil, errors.New("a página não trouxe projetos (o layout pode ter mudado)")
	}

	var jobs []domain.Job
	for _, pr := range data.Results {
		age, ok := workanaAge(pr.Published)
		if pr.Slug == "" || !ok || age > freelanceMaxAge {
			continue
		}
		bidsText := reWorkanaNumber.FindString(pr.TotalBids)
		bids, err := strconv.Atoi(bidsText)
		if err != nil || bids > freelanceMaxBids || !workanaBudgetOK(pr.Budget, pr.IsHourly) {
			continue
		}

		title := cleanText(pr.Title)
		if t := reWorkanaTitle.FindStringSubmatch(pr.Title); t != nil {
			title = cleanText(t[1])
		}
		budget := pr.Budget
		if pr.IsHourly {
			budget += " (por hora)"
		}
		if pr.Verified {
			budget += " · pagamento verificado"
		}
		skills := make([]string, 0, len(pr.Skills))
		for _, s := range pr.Skills {
			skills = append(skills, cleanText(s.Name))
		}

		jobs = append(jobs, freelanceListing{
			source:      "workana",
			platform:    "Workana",
			url:         "https://www.workana.com/job/" + pr.Slug,
			title:       title,
			description: cleanText(pr.Description),
			budget:      budget,
			skills:      skills,
			bids:        bids,
			published:   now.Add(-age),
		}.toJob(now))
	}
	return jobs, nil
}

// workanaAge lê datas relativas ("Agora mesmo", "há 14 minutos", "há 2 horas").
// "Ontem" ou mais antigo é descartado: com varreduras frequentes, o projeto já foi visto antes.
func workanaAge(s string) (time.Duration, bool) {
	s = strings.ToLower(s)
	if strings.Contains(s, "agora") {
		return 0, true
	}
	m := reWorkanaAgeAmount.FindStringSubmatch(s)
	if m == nil {
		return 0, false
	}
	n, _ := strconv.Atoi(m[1])
	if m[2] == "hora" {
		return time.Duration(n) * time.Hour, true
	}
	return time.Duration(n) * time.Minute, true
}

// workanaBudgetOK aplica o mínimo ao meio da faixa ("USD 500 - 1.000").
// Faixas em outra moeda não são convertidas e passam sem esse corte.
func workanaBudgetOK(budget string, hourly bool) bool {
	if !strings.Contains(budget, "USD") {
		return true
	}
	var values []float64
	for _, n := range reWorkanaNumber.FindAllString(budget, -1) {
		if v, err := strconv.ParseFloat(strings.ReplaceAll(n, ".", ""), 64); err == nil {
			values = append(values, v)
		}
	}
	if len(values) == 0 {
		return false
	}
	// "Menos de USD 50": o número é o teto
	if strings.Contains(strings.ToLower(budget), "menos") {
		values = []float64{values[0] / 2}
	}
	mid := (values[0] + values[len(values)-1]) / 2
	if hourly {
		return mid >= freelancerMinHourlyUSD
	}
	return mid >= freelancerMinFixedUSD
}
