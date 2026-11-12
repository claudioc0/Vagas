package provider

import (
	"context"
	"vagas-go/internal/domain"
)

// Provider define o contrato para qualquer fonte de vagas (API, RSS, Scraper, IMAP)
type Provider interface {
	ID() string
	Name() string
	Fetch(ctx context.Context) ([]domain.Job, error)
}
