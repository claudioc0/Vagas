package provider

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"time"
	"vagas-go/internal/domain"
)

// Cortes comuns às fontes de projetos freelance
const (
	freelanceMaxBids = 30
	freelanceMaxAge  = 24 * time.Hour
)

// freelanceSource marca fontes em que "nenhum projeto passou nos filtros" é normal:
// falha de leitura é devolvida como erro pelo próprio provedor.
type freelanceSource struct{}

func (freelanceSource) MayBeEmpty() bool { return true }

type freelanceListing struct {
	source, platform, url, title, description, budget string
	skills                                           []string
	bids                                             int
	published                                        time.Time
}

func (l freelanceListing) toJob(now time.Time) domain.Job {
	job := domain.Job{
		SourceID: l.source,
		Title:    l.title,
		Company:  l.platform,
		// Para projetos, a localização guarda orçamento e concorrência
		Location:    fmt.Sprintf("%s · %d propostas", l.budget, l.bids),
		Modality:    domain.ModalityRemote,
		Seniority:   domain.SeniorityFreelance,
		URL:         l.url,
		Description: truncateDesc(l.description),
		Skills:      l.skills,
		Bids:        l.bids,
		PublishedAt: l.published,
		CollectedAt: now,
	}
	job.ID = job.GenerateID()
	return job
}

func fetchHTML(ctx context.Context, client *http.Client, pageURL string) (string, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, pageURL, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VagasHunter/1.0")
	req.Header.Set("Accept", "text/html")

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("status %d", resp.StatusCode)
	}
	body, err := io.ReadAll(io.LimitReader(resp.Body, 8<<20))
	return string(body), err
}
