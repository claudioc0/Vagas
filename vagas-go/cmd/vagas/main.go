package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/spf13/cobra"
	"vagas-go/internal/domain"
	"vagas-go/internal/notifier"
	"vagas-go/internal/pipeline"
	"vagas-go/internal/provider"
	"vagas-go/internal/storage"
	"vagas-go/internal/ui/tui"
)

var (
	dbPath      string
	minScore    int
	modalityStr string
	searchQuery string
	limitCount  int
	reportPath  string
)

func main() {
	defaultDB := filepath.Join("..", "vagas.db")
	defaultReport := filepath.Join("..", "busca", "radar_vagas_recomendadas.md")

	rootCmd := &cobra.Command{
		Use:   "vagas",
		Short: "vagas-go: Rastreador Concorrente de Vagas Tech & Gestor de Candidaturas",
		Long:  "Sistema em Go de alta performance para busca concorrente, filtragem estrita e gestão de vagas tech.",
	}

	rootCmd.PersistentFlags().StringVar(&dbPath, "db", defaultDB, "Caminho do arquivo SQLite (vagas.db)")

	// Subcomando: tui
	tuiCmd := &cobra.Command{
		Use:   "tui",
		Short: "Abre a interface gráfica interativa no terminal (Bubbletea)",
		RunE: func(cmd *cobra.Command, args []string) error {
			db, err := storage.Open(dbPath)
			if err != nil {
				return fmt.Errorf("erro ao abrir banco: %w", err)
			}
			defer db.Close()

			return tui.RunTUI(db)
		},
	}

	// Subcomando: scan
	scanCmd := &cobra.Command{
		Use:   "scan",
		Short: "Executa varredura concorrente em todas as fontes configuradas",
		RunE: func(cmd *cobra.Command, args []string) error {
			db, err := storage.Open(dbPath)
			if err != nil {
				return fmt.Errorf("erro ao abrir banco: %w", err)
			}
			defer db.Close()

			fmt.Println("🚀 Iniciando varredura paralela de vagas em Go...")
			gh := provider.NewGitHubProvider()
			rem := provider.NewRemotarProvider()

			engine := pipeline.NewEngine(db, gh, rem)

			ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
			defer cancel()

			stats, err := engine.Run(ctx, false)
			if err != nil {
				return fmt.Errorf("erro no pipeline: %w", err)
			}

			stats.PrintSummary()

			// Notificação no Telegram se configurado
			tel := notifier.NewTelegramNotifier(db)
			if tel.IsConfigured() {
				fmt.Println("📲 Verificando alertas do Telegram...")
				jobs, _ := db.ListJobs(ctx, storage.JobFilter{MinScore: 80, Limit: 10})
				sent, err := tel.NotifyHotJobs(ctx, jobs, 80)
				if err != nil {
					fmt.Printf("  [Telegram] Aviso: %v\n", err)
				} else if sent > 0 {
					fmt.Printf("  -> %d nova(s) vaga(s) quente(s) enviada(s) ao Telegram!\n", sent)
				} else {
					fmt.Println("  -> Nenhuma vaga nova pendente de envio para o Telegram.")
				}
			}

			// Geração automática do relatório Markdown
			if reportPath != "" {
				_ = pipeline.GenerateMarkdownReport(ctx, db, reportPath)
				fmt.Printf("📄 Relatório atualizado em: %s\n", reportPath)
			}

			return nil
		},
	}
	scanCmd.Flags().StringVar(&reportPath, "report", defaultReport, "Caminho do relatório Markdown a ser gerado")

	// Subcomando: list
	listCmd := &cobra.Command{
		Use:   "list",
		Short: "Lista vagas armazenadas no banco aplicando filtros",
		RunE: func(cmd *cobra.Command, args []string) error {
			db, err := storage.Open(dbPath)
			if err != nil {
				return fmt.Errorf("erro ao abrir banco: %w", err)
			}
			defer db.Close()

			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()

			filter := storage.JobFilter{
				MinScore: minScore,
				Modality: domain.Modality(modalityStr),
				Search:   searchQuery,
				Limit:    limitCount,
			}

			jobs, err := db.ListJobs(ctx, filter)
			if err != nil {
				return fmt.Errorf("erro ao consultar vagas: %w", err)
			}

			if len(jobs) == 0 {
				fmt.Println("Nenhuma vaga encontrada com os filtros especificados.")
				return nil
			}

			fmt.Printf("\n%-6s | %-20s | %-35s | %-10s | %-25s\n", "SCORE", "EMPRESA", "TÍTULO", "MODALIDADE", "TAGS")
			fmt.Println(strings.Repeat("-", 105))

			for _, j := range jobs {
				tags := strings.Join(j.Tags, ", ")
				if len(tags) > 23 {
					tags = tags[:23] + ".."
				}

				title := j.Title
				if len(title) > 33 {
					title = title[:33] + ".."
				}

				comp := j.Company
				if len(comp) > 18 {
					comp = comp[:18] + ".."
				}

				fmt.Printf("[%3d%%] | %-20s | %-35s | %-10s | %-25s\n", j.FitScore, comp, title, j.Modality, tags)
				fmt.Printf("       🔗 %s\n", j.URL)
				if j.FitReason != "" {
					fmt.Printf("       💡 %s\n", j.FitReason)
				}
				fmt.Println(strings.Repeat(".", 105))
			}

			fmt.Printf("\nTotal exibido: %d vagas.\n", len(jobs))
			return nil
		},
	}

	listCmd.Flags().IntVarP(&minScore, "min-score", "s", 60, "Pontuação mínima de Fit Score")
	listCmd.Flags().StringVarP(&modalityStr, "modality", "m", "", "Filtrar por modalidade (Remoto, Presencial, Híbrido)")
	listCmd.Flags().StringVarP(&searchQuery, "search", "q", "", "Busca por termo no título, empresa ou tags")
	listCmd.Flags().IntVarP(&limitCount, "limit", "l", 20, "Limite de resultados")

	// Subcomando: stats
	statsCmd := &cobra.Command{
		Use:   "stats",
		Short: "Exibe o total acumulado de vagas e índice de elegibilidade",
		RunE: func(cmd *cobra.Command, args []string) error {
			db, err := storage.Open(dbPath)
			if err != nil {
				return fmt.Errorf("erro ao abrir banco: %w", err)
			}
			defer db.Close()

			ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
			defer cancel()

			total, elegiveis, err := db.CountJobs(ctx)
			if err != nil {
				return fmt.Errorf("erro ao contar vagas: %w", err)
			}

			fmt.Println("📊 Estatísticas do Banco de Vagas:")
			fmt.Printf("  • Total de Vagas Cadastradas : %d\n", total)
			fmt.Printf("  • Vagas Elegíveis (Score >=60): %d\n", elegiveis)
			if total > 0 {
				fmt.Printf("  • Taxa de Elegibilidade       : %.1f%%\n", (float64(elegiveis)/float64(total))*100)
			}
			return nil
		},
	}

	rootCmd.AddCommand(tuiCmd, scanCmd, listCmd, statsCmd)

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
