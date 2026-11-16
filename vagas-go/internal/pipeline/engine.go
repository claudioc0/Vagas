package pipeline

import (
	"context"
	"fmt"
	"sort"
	"strings"
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
	// Warnings reúne falhas de fontes/persistência que não interrompem a varredura
	Warnings []string `json:"warnings,omitempty"`
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
	var warnMu sync.Mutex
	upsertErrs := 0
	var firstUpsertErr error
	addWarning := func(w string) {
		warnMu.Lock()
		stats.Warnings = append(stats.Warnings, w)
		warnMu.Unlock()
	}

	// Goroutine consumidora (Fan-In): apenas coleta; o processamento ocorre depois,
	// em ordem determinística, para que a mesma vaga vinda de várias fontes
	// (ex.: Remotar e Gupy) fique sempre com o mesmo registro/ID entre execuções.
	var collected []domain.Job
	processWG.Add(1)
	go func() {
		defer processWG.Done()
		for job := range jobsChan {
			collected = append(collected, job)
		}
	}()

	process := func() {
		sort.SliceStable(collected, func(i, k int) bool {
			return sourcePriority(collected[i].SourceID) < sourcePriority(collected[k].SourceID)
		})
		for _, job := range collected {
			stats.TotalFound++

			key := job.DedupKey()
			mapMu.Lock()
			if seenMap[key] {
				mapMu.Unlock()
				continue
			}
			seenMap[key] = true
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
			if _, err := e.db.UpsertJob(ctx, &job); err != nil {
				upsertErrs++
				if firstUpsertErr == nil {
					firstUpsertErr = err
				}
			}
		}
	}

	// Executa os provedores em paralelo (Fan-Out)
	g, gCtx := errgroup.WithContext(ctx)

	for _, p := range e.providers {
		prov := p
		g.Go(func() error {
			jobs, err := prov.Fetch(gCtx)
			// Falha em uma fonte não interrompe as demais, mas é registrada
			if err != nil {
				fmt.Printf("  [Aviso] Fonte %s com falhas: %v\n", prov.ID(), err)
				addWarning(fmt.Sprintf("Fonte %s com falhas: %s", prov.ID(), firstLine(err.Error())))
			} else if len(jobs) == 0 {
				fmt.Printf("  [Aviso] Fonte %s retornou 0 vagas\n", prov.ID())
				addWarning(fmt.Sprintf("Fonte %s retornou 0 vagas", prov.ID()))
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
	process()

	if upsertErrs > 0 {
		fmt.Printf("  [Aviso] %d vaga(s) não persistidas no banco: %v\n", upsertErrs, firstUpsertErr)
		stats.Warnings = append(stats.Warnings, fmt.Sprintf("%d vaga(s) não persistidas (%v)", upsertErrs, firstUpsertErr))
	}

	stats.Duration = time.Since(start)
	return stats, nil
}

// sourcePriority define qual fonte "vence" na deduplicação (menor = preferida).
// A Gupy fica por último porque o Remotar já agrega vagas dela, e os registros
// do Remotar existentes no banco não devem ser duplicados nem renotificados.
func sourcePriority(source string) int {
	if source == "gupy" {
		return 1
	}
	return 0
}

func firstLine(s string) string {
	if i := strings.IndexByte(s, '\n'); i >= 0 {
		return s[:i]
	}
	return s
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
