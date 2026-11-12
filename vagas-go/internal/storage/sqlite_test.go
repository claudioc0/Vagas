package storage_test

import (
	"context"
	"path/filepath"
	"testing"
	"time"
	"vagas-go/internal/domain"
	"vagas-go/internal/storage"
)

func TestSQLiteStorage(t *testing.T) {
	tempDB := filepath.Join(t.TempDir(), "test_vagas.db")
	db, err := storage.Open(tempDB)
	if err != nil {
		t.Fatalf("Erro ao abrir banco: %v", err)
	}
	defer db.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	job := &domain.Job{
		SourceID:    "github_backendbr",
		Title:       "Desenvolvedor Go Júnior",
		Company:     "Acme Dev",
		Location:    "Remoto",
		Modality:    domain.ModalityRemote,
		Seniority:   "Júnior",
		URL:         "https://github.com/backend-br/vagas/issues/999",
		Description: "Vaga para desenvolvedor Go backend júnior",
		Tags:        []string{"Go", "Docker", "SQL"},
		FitScore:    95,
		FitReason:   "Match excelente",
		PublishedAt: time.Now(),
		CollectedAt: time.Now(),
	}
	job.ID = job.GenerateID()

	// 1. Inserir Vaga
	inserted, err := db.UpsertJob(ctx, job)
	if err != nil {
		t.Fatalf("Erro ao inserir vaga: %v", err)
	}
	if !inserted {
		t.Errorf("Esperava inserted=true")
	}

	// 2. Listar Vagas
	jobs, err := db.ListJobs(ctx, storage.JobFilter{MinScore: 80})
	if err != nil {
		t.Fatalf("Erro ao listar vagas: %v", err)
	}
	if len(jobs) != 1 {
		t.Fatalf("Esperava 1 vaga retornada, obteve %d", len(jobs))
	}
	if jobs[0].Company != "Acme Dev" {
		t.Errorf("Empresa incorreta: %s", jobs[0].Company)
	}

	// 3. Contagem
	total, elegiveis, err := db.CountJobs(ctx)
	if err != nil {
		t.Fatalf("Erro ao contar: %v", err)
	}
	if total != 1 || elegiveis != 1 {
		t.Errorf("Contagem incorreta: total=%d, elegiveis=%d", total, elegiveis)
	}
}
