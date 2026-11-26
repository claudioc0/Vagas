package pipeline

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
	"vagas-go/internal/storage"
	"vagas-go/pkg/fitscore"
)

// GenerateMarkdownReport cria o arquivo radar_vagas_recomendadas.md atualizado
func GenerateMarkdownReport(ctx context.Context, db *storage.DB, outputPath string) error {
	jobs, err := db.ListJobs(ctx, storage.JobFilter{MinScore: 60, Limit: 50, ExcludeFreelance: true})
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

	// Nível B: tecnologia sem nível declarado, com sinais de entrada (apenas para revisão manual)
	tierB, err := db.ListJobs(ctx, storage.JobFilter{ReasonPrefix: fitscore.TierBReason, Limit: 30})
	if err != nil {
		return err
	}
	if len(tierB) > 0 {
		sb.WriteString("\n---\n\n## 🔍 Para Revisar (nível não declarado)\n\n")
		sb.WriteString("> Vagas de tecnologia sem \"júnior\" no anúncio, mas com sinais de nível de entrada e sem indícios de senioridade. Não geram alerta no Telegram.\n\n")
		sb.WriteString("| Empresa | Título da Vaga | Modalidade | Tecnologias | Link |\n")
		sb.WriteString("| :--- | :--- | :---: | :--- | :---: |\n")
		for _, j := range tierB {
			tags := strings.Join(j.Tags, ", ")
			if tags == "" {
				tags = "-"
			}
			sb.WriteString(fmt.Sprintf("| %s | %s | %s | `%s` | [Ver vaga](%s) |\n",
				strings.ReplaceAll(j.Company, "|", "-"), strings.ReplaceAll(j.Title, "|", "-"), j.Modality, tags, j.URL))
		}
	}

	// Projetos fecham rápido: só os publicados nos últimos 3 dias
	freelas, err := db.ListJobs(ctx, storage.JobFilter{MinScore: 50, Limit: 30, OnlyFreelance: true, PublishedSince: time.Now().Add(-72 * time.Hour)})
	if err != nil {
		return err
	}
	if len(freelas) > 0 {
		sb.WriteString("\n---\n\n## 💼 Projetos Freelance\n\n")
		sb.WriteString("> Orçamento e número de propostas são os da última coleta em que o projeto passou nos filtros.\n\n")
		sb.WriteString("| Fit | Projeto | Orçamento e propostas | Publicado | Link |\n")
		sb.WriteString("| :---: | :--- | :--- | :---: | :---: |\n")
		for _, j := range freelas {
			sb.WriteString(fmt.Sprintf("| %d%% | %s | %s | %s | [Ver projeto](%s) |\n",
				j.FitScore, strings.ReplaceAll(j.Title, "|", "-"), j.Location, j.PublishedAt.Format("02/01 15:04"), j.URL))
		}
	}

	sb.WriteString("\n---\n")
	sb.WriteString("*(Relatório gerado automaticamente pelo motor de alta performance em Go)*\n")

	return os.WriteFile(outputPath, []byte(sb.String()), 0644)
}
