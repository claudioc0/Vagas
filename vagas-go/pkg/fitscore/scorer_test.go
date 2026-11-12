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
