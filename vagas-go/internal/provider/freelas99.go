package provider

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"
	"vagas-go/internal/domain"
)

// 99Freelas: listagem renderizada no servidor (o robots.txt não restringe).
// A lista não informa orçamento, então valem apenas os cortes de idade e propostas.
const freelas99Pages = 3

var (
	re99Item      = regexp.MustCompile(`<li class="[^"]*result-item[^"]*"`)
	re99Title     = regexp.MustCompile(`(?s)<h1 class="title">\s*<a href="(/project/[^"?]+)[^"]*">(.*?)</a>`)
	re99Info      = regexp.MustCompile(`(?s)<p class="item-text information">(.*?)<(?:b class="datetime"|/p>)`)
	re99Published = regexp.MustCompile(`class="datetime" cp-datetime="(\d+)"`)
	re99Bids      = regexp.MustCompile(`Propostas:\s*<b>(\d+)</b>`)
	re99Desc      = regexp.MustCompile(`(?s)class="item-text description[^"]*" data-content="[^"]*">(.*?)</div>`)
	re99Skill     = regexp.MustCompile(`class="habilidade[^"]*"[^>]*>([^<]+)<`)
	// A categoria "web, mobile e software" também lista projetos de design
	re99DesignCategory = regexp.MustCompile(`(?i)(design|ux)`)
)

type Freelas99Provider struct {
	freelanceSource
	client *http.Client
}

func NewFreelas99Provider() *Freelas99Provider {
	return &Freelas99Provider{client: &http.Client{Timeout: 15 * time.Second}}
}

func (p *Freelas99Provider) ID() string   { return "99freelas" }
func (p *Freelas99Provider) Name() string { return "99Freelas (Projetos)" }

func (p *Freelas99Provider) Fetch(ctx context.Context) ([]domain.Job, error) {
	var (
		all  []domain.Job
		errs []error
		seen = make(map[string]bool)
	)
	now := time.Now()
	for page := 1; page <= freelas99Pages; page++ {
		u := "https://www.99freelas.com.br/projects?categoria=web-mobile-e-software"
		if page > 1 {
			u += fmt.Sprintf("&page=%d", page)
		}
		body, err := fetchHTML(ctx, p.client, u)
		if err != nil {
			errs = append(errs, fmt.Errorf("página %d: %w", page, err))
			continue
		}
		jobs, parsed := parse99Freelas(body, now)
		if parsed == 0 {
			errs = append(errs, fmt.Errorf("página %d: nenhum projeto reconhecido (o layout pode ter mudado)", page))
		}
		for _, j := range jobs {
			if !seen[j.ID] {
				seen[j.ID] = true
				all = append(all, j)
			}
		}
	}
	return all, errors.Join(errs...)
}

// parse99Freelas devolve os projetos aprovados e quantos cartões foram lidos por completo.
func parse99Freelas(body string, now time.Time) ([]domain.Job, int) {
	starts := re99Item.FindAllStringIndex(body, -1)
	var jobs []domain.Job
	parsed := 0
	for i, start := range starts {
		end := len(body)
		if i+1 < len(starts) {
			end = starts[i+1][0]
		}
		card := body[start[0]:end]

		title := re99Title.FindStringSubmatch(card)
		published := re99Published.FindStringSubmatch(card)
		bidsM := re99Bids.FindStringSubmatch(card)
		if title == nil || published == nil || bidsM == nil {
			continue
		}
		parsed++

		millis, _ := strconv.ParseInt(published[1], 10, 64)
		when := time.UnixMilli(millis)
		bids, _ := strconv.Atoi(bidsM[1])
		if now.Sub(when) > freelanceMaxAge || bids > freelanceMaxBids {
			continue
		}
		if info := re99Info.FindStringSubmatch(card); info != nil {
			category, _, _ := strings.Cut(cleanText(info[1]), "|")
			if re99DesignCategory.MatchString(category) {
				continue
			}
		}

		budget := "Orçamento não informado"
		if strings.Contains(card, `title="Projeto exclusivo`) {
			budget += " · exclusivo para assinantes"
		}
		var skills []string
		for _, s := range re99Skill.FindAllStringSubmatch(card, -1) {
			skills = append(skills, cleanText(s[1]))
		}
		desc := ""
		if m := re99Desc.FindStringSubmatch(card); m != nil {
			desc = cleanText(m[1])
		}

		jobs = append(jobs, freelanceListing{
			source:      "99freelas",
			platform:    "99Freelas",
			url:         "https://www.99freelas.com.br" + title[1],
			title:       cleanText(title[2]),
			description: desc,
			budget:      budget,
			skills:      skills,
			bids:        bids,
			published:   when,
		}.toJob(now))
	}
	return jobs, parsed
}
