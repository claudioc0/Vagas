package pipeline

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
	"vagas-go/internal/storage"
)

// GenerateMarkdownReport cria o arquivo radar_vagas_recomendadas.md atualizado
func GenerateMarkdownReport(ctx context.Context, db *storage.DB, outputPath string) error {
	jobs, err := db.ListJobs(ctx, storage.JobFilter{MinScore: 60, Limit: 50})
	if err != nil {
		return err
	}

	total, elegiveis, _ := db.CountJobs(ctx)

	dir := filepath.Dir(outputPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	var sb strings.Builder
	nowStr := time.Now().Format("02/01/2006 às 15:04")

	sb.WriteString("# 🎯 Radar Automatizado de Vagas Tech (Go Engine)\n\n")
	sb.WriteString(fmt.Sprintf("> **Última Atualização:** %s (Executado via GitHub Actions / Go Engine)\n", nowStr))
	sb.WriteString(fmt.Sprintf("> **Total no Banco:** %d vagas | **Elegíveis (Score >= 60):** %d vagas\n\n", total, elegiveis))
	sb.WriteString("---\n\n")

	sb.WriteString("## 🔥 Melhores Oportunidades Encontradas\n\n")
	sb.WriteString("| Fit | Empresa | Título da Vaga | Modalidade | Tecnologias | Link |\n")
	sb.WriteString("| :---: | :--- | :--- | :---: | :--- | :---: |\n")

	for _, j := range jobs {
		tags := strings.Join(j.Tags, ", ")
		if tags == "" {
			tags = "-"
		}
		cleanTitle := strings.ReplaceAll(j.Title, "|", "-")
		cleanCompany := strings.ReplaceAll(j.Company, "|", "-")

		sb.WriteString(fmt.Sprintf(
			"| **%d%%** | %s | %s | %s | `%s` | [Candidatar-se](%s) |\n",
			j.FitScore, cleanCompany, cleanTitle, j.Modality, tags, j.URL,
		))
	}

	sb.WriteString("\n---\n")
	sb.WriteString("*(Relatório gerado automaticamente pelo motor de alta performance em Go)*\n")

	return os.WriteFile(outputPath, []byte(sb.String()), 0644)
}
