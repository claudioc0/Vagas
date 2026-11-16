package fitscore_test

import (
	"testing"
	"vagas-go/internal/domain"
	"vagas-go/pkg/fitscore"
)

func TestEvaluate(t *testing.T) {
	tests := []struct {
		name          string
		job           domain.Job
		expectedScore int
		mustBeZero    bool
	}{
		{
			name: "Vaga Jr Go Remoto Elegivel",
			job: domain.Job{
				Title:       "Desenvolvedor Go Júnior",
				Company:     "TechCorp",
				Modality:    domain.ModalityRemote,
				Description: "Conhecimento em Golang, Docker e SQL",
			},
			mustBeZero: false,
		},
		{
			name: "Vaga Pleno Desqualificada",
			job: domain.Job{
				Title:       "Desenvolvedor Pleno Python",
				Company:     "Alpha Inc",
				Modality:    domain.ModalityRemote,
				Description: "Django e FastAPI",
			},
			mustBeZero: true,
		},
		{
			name: "Vaga Estágio Desqualificada",
			job: domain.Job{
				Title:       "Estágio em Desenvolvimento de Software",
				Company:     "Beta Soft",
				Modality:    domain.ModalityRemote,
				Description: "Cursando graduação",
			},
			mustBeZero: true,
		},
		{
			name: "Vaga Suporte Nao Core",
			job: domain.Job{
				Title:       "Analista de Suporte e Help Desk Jr",
				Company:     "SupportCo",
				Modality:    domain.ModalityRemote,
				Description: "Atendimento ao cliente",
			},
			mustBeZero: true,
		},
	}

	onsite := func(loc string, mod domain.Modality) domain.Job {
		return domain.Job{Title: "Desenvolvedor Python Júnior", Company: "X", Location: loc, Modality: mod}
	}
	tests = append(tests, []struct {
		name          string
		job           domain.Job
		expectedScore int
		mustBeZero    bool
	}{
		{"Presencial Curitiba ok", onsite("Curitiba, Paraná", domain.ModalityOnSite), 0, false},
		{"Hibrido Sao Jose dos Pinhais ok", onsite("São José dos Pinhais, Paraná", domain.ModalityHybrid), 0, false},
		{"Presencial PR sigla ok", onsite("Londrina - PR", domain.ModalityOnSite), 0, false},
		{"Presencial local desconhecido ok", onsite("Brasil", domain.ModalityOnSite), 0, false},
		{"Presencial Presidente Prudente fora", onsite("Presidente Prudente, São Paulo", domain.ModalityOnSite), 0, true},
		{"Hibrido Salvador fora", onsite("Salvador, Bahia", domain.ModalityHybrid), 0, true},
		{"Hibrido Sao Paulo fora", onsite("São Paulo, São Paulo", domain.ModalityHybrid), 0, true},
		{"Remoto fora do PR ok", onsite("Salvador, Bahia", domain.ModalityRemote), 0, false},
	}...)

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			score, reason, tags := fitscore.Evaluate(&tt.job)
			if tt.mustBeZero && score != 0 {
				t.Errorf("Esperava score 0, obteve %d (motivo: %s)", score, reason)
			}
			if !tt.mustBeZero && score < 50 {
				t.Errorf("Esperava score >= 50, obteve %d (motivo: %s)", score, reason)
			}
			t.Logf("[%s] Score: %d | Tags: %v | Razao: %s", tt.name, score, tags, reason)
		})
	}
}
