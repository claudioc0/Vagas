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

// maxDescLen limita a descrição guardada; longa o bastante para o scorer enxergar
// requisitos como "sem experiência" ou "3+ anos".
const maxDescLen = 2000

// truncateDesc corta a descrição sem quebrar caracteres multibyte.
func truncateDesc(s string) string {
	if r := []rune(s); len(r) > maxDescLen {
		return string(r[:maxDescLen]) + "..."
	}
	return s
}
