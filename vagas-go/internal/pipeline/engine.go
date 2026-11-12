package pipeline

import (
	"context"
	"fmt"
	"sync"
	"time"
	"vagas-go/internal/domain"
	"vagas-go/internal/provider"
	"vagas-go/internal/storage"
	"vagas-go/pkg/fitscore"

	"golang.org/x/sync/errgroup"
)

// ScanStats armazena métricas da rodada de busca
type ScanStats struct {
	TotalFound   int           `json:"total_found"`
	TotalUnique  int           `json:"total_unique"`
	Eligible     int           `json:"eligible"`
	HighFit      int           `json:"high_fit"`
	Duration     time.Duration `json:"duration"`
	ProviderHits map[string]int `json:"provider_hits"`
}

// Engine orquestra a coleta paralela e persistência
type Engine struct {
	db        *storage.DB
	providers []provider.Provider
}

// NewEngine instancia o orquestrador
func NewEngine(db *storage.DB, providers ...provider.Provider) *Engine {
	return &Engine{
		db:        db,
		providers: providers,
	}
}

// Run executa todas as fontes em paralelo com fan-in de resultados
func (e *Engine) Run(ctx context.Context, onlyEligible bool) (*ScanStats, error) {
	start := time.Now()
	stats := &ScanStats{
		ProviderHits: make(map[string]int),
	}

	jobsChan := make(chan domain.Job, 200)
	var processWG sync.WaitGroup
	seenMap := make(map[string]bool)
	var mapMu sync.Mutex

	// Goroutine consumidora (Fan-In): Deduplica, pontua e persiste
	processWG.Add(1)
	go func() {
		defer processWG.Done()
		for job := range jobsChan {
			stats.TotalFound++

			mapMu.Lock()
			if seenMap[job.ID] {
				mapMu.Unlock()
				continue
			}
			seenMap[job.ID] = true
			mapMu.Unlock()

			stats.TotalUnique++
			stats.ProviderHits[job.SourceID]++

			// Avaliação com Fit Score estrito
			score, reason, tags := fitscore.Evaluate(&job)
			job.FitScore = score
			job.FitReason = reason
			job.Tags = tags

			if score >= 50 {
				stats.Eligible++
			}
			if score >= 75 {
				stats.HighFit++
			}

			// Se onlyEligible for true, só grava no banco se score > 0
			if onlyEligible && score == 0 {
				continue
			}

			// Persistência no SQLite
			_, _ = e.db.UpsertJob(ctx, &job)
		}
	}()

	// Executa os provedores em paralelo (Fan-Out)
	g, gCtx := errgroup.WithContext(ctx)

	for _, p := range e.providers {
		prov := p
		g.Go(func() error {
			jobs, err := prov.Fetch(gCtx)
			if err != nil {
				return nil // Falha em uma fonte não interrompe as demais
			}
			for _, j := range jobs {
				select {
				case jobsChan <- j:
				case <-gCtx.Done():
					return gCtx.Err()
				}
			}
			return nil
		})
	}

	// Aguarda todos os provedores terminarem
	_ = g.Wait()
	close(jobsChan)

	// Aguarda processamento de persistência
	processWG.Wait()

	stats.Duration = time.Since(start)
	return stats, nil
}

// PrintSummary exibe um resumo formatado da varredura
func (s *ScanStats) PrintSummary() {
	fmt.Printf("\n=== Varredura Concluída em %v ===\n", s.Duration.Round(time.Millisecond))
	fmt.Printf("Total de Vagas Brutas : %d\n", s.TotalFound)
	fmt.Printf("Total Vagas Únicas    : %d\n", s.TotalUnique)
	fmt.Printf("Vagas Elegíveis (>=50): %d\n", s.Eligible)
	fmt.Printf("Alto Fit (Score >=75) : %d\n", s.HighFit)
	fmt.Println("Distribuição por Fonte:")
	for prov, count := range s.ProviderHits {
		fmt.Printf("  • %-20s: %d\n", prov, count)
	}
	fmt.Println("========================================")
}
