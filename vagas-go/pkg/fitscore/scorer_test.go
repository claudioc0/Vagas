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
		{"Analista de Sistemas Junior remoto", domain.Job{Title: "Analista de Sistemas Junior", Company: "X", Location: "Brasil", Modality: domain.ModalityRemote}, 0, false},
		{"Trainee TI remoto", domain.Job{Title: "Trainee | Tecnologia da Informação (TI)", Company: "X", Modality: domain.ModalityRemote}, 0, false},
		{"Advogado Junior continua fora", domain.Job{Title: "Advogado(a) Junior - Direito Digital", Company: "X", Modality: domain.ModalityRemote}, 0, true},
		{"Analista Financeiro Junior continua fora", domain.Job{Title: "Analista Financeiro - Júnior", Company: "X", Modality: domain.ModalityRemote}, 0, true},
		{"Nivel B sem sinal de entrada fora", domain.Job{Title: "Desenvolvedor(a) Full Stack", Company: "X", Location: "Brasil", Modality: domain.ModalityRemote, Description: "Construir APIs em Go"}, 0, true},
		{"Nivel B exige anos fora", domain.Job{Title: "Desenvolvedor(a) Backend", Company: "X", Location: "Brasil", Modality: domain.ModalityRemote, Description: "Early career mas com 4 anos de experiência"}, 0, true},
		{"Nivel B arquiteto fora", domain.Job{Title: "Arquiteto de Soluções de IA", Company: "X", Location: "Brasil", Modality: domain.ModalityRemote, Description: "early career"}, 0, true},
		{"Nivel B fora do remoto fora", domain.Job{Title: "Software Engineer", Company: "X", Location: "Cidade do México", Modality: domain.ModalityUnknown, Description: "Early Career"}, 0, true},
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

func TestEvaluateTierB(t *testing.T) {
	job := domain.Job{
		Title: "Desenvolvedor(a) Full Stack", Company: "X", Location: "Brasil",
		Modality: domain.ModalityRemote, Description: "Não exigimos experiência prévia. Stack: Python e React.",
	}
	score, reason, _ := fitscore.Evaluate(&job)
	if score < 35 || score > 49 {
		t.Fatalf("Nível B deveria ter score entre 35 e 49, obteve %d (%s)", score, reason)
	}
	if len(reason) < len(fitscore.TierBReason) || reason[:len(fitscore.TierBReason)] != fitscore.TierBReason {
		t.Errorf("motivo inesperado: %s", reason)
	}

	// Nível A continua >= 50
	jr := job
	jr.Title = "Desenvolvedor(a) Full Stack Júnior"
	if s, _, _ := fitscore.Evaluate(&jr); s < 50 {
		t.Errorf("Nível A deveria ser >= 50, obteve %d", s)
	}
}
