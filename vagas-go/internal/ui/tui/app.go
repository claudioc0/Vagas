package tui

import (
	"context"
	"fmt"
	"os/exec"
	"runtime"
	"strings"

	"github.com/charmbracelet/bubbles/table"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"vagas-go/internal/domain"
	"vagas-go/internal/storage"
)

var (
	baseStyle = lipgloss.NewStyle().
			BorderStyle(lipgloss.NormalBorder()).
			BorderForeground(lipgloss.Color("240"))

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FAFAFA")).
			Background(lipgloss.Color("#7D56F4")).
			PaddingLeft(2).
			PaddingRight(2).
			MarginBottom(1)

	detailStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("#7D56F4")).
			Padding(1).
			Width(80)

	greenScore = lipgloss.NewStyle().Foreground(lipgloss.Color("#04B575")).Bold(true)
	yellowScore = lipgloss.NewStyle().Foreground(lipgloss.Color("#FFCC00")).Bold(true)
)

type Model struct {
	table table.Model
	jobs  []domain.Job
	db    *storage.DB
	msg   string
}

func NewModel(db *storage.DB) (Model, error) {
	ctx := context.Background()
	jobs, err := db.ListJobs(ctx, storage.JobFilter{MinScore: 0, Limit: 100})
	if err != nil {
		return Model{}, err
	}

	columns := []table.Column{
		{Title: "FIT", Width: 7},
		{Title: "EMPRESA", Width: 20},
		{Title: "TÍTULO DA VAGA", Width: 38},
		{Title: "MODALIDADE", Width: 12},
		{Title: "TAGS", Width: 25},
	}

	var rows []table.Row
	for _, j := range jobs {
		tagStr := strings.Join(j.Tags, ", ")
		rows = append(rows, table.Row{
			fmt.Sprintf("%d%%", j.FitScore),
			j.Company,
			j.Title,
			string(j.Modality),
			tagStr,
		})
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithRows(rows),
		table.WithFocused(true),
		table.WithHeight(14),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240")).
		BorderBottom(true).
		Bold(true)
	s.Selected = s.Selected.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("57")).
		Bold(true)
	t.SetStyles(s)

	return Model{
		table: t,
		jobs:  jobs,
		db:    db,
		msg:   "Use [↑/↓] para navegar, [Enter] para abrir vaga no navegador, [q] para sair.",
	}, nil
}

func (m Model) Init() tea.Cmd {
	return nil
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c", "esc":
			return m, tea.Quit
		case "enter":
			cursor := m.table.Cursor()
			if cursor >= 0 && cursor < len(m.jobs) {
				job := m.jobs[cursor]
				openBrowser(job.URL)
				m.msg = fmt.Sprintf("🌐 Abrindo no navegador: %s", job.Title)
			}
		}
	}

	m.table, cmd = m.table.Update(msg)
	return m, cmd
}

func (m Model) View() string {
	title := titleStyle.Render("🎯 VAGAS-GO — RADAR CONCORRENTE DE OPORTUNIDADES")
	view := title + "\n" + baseStyle.Render(m.table.View()) + "\n"

	cursor := m.table.Cursor()
	if cursor >= 0 && cursor < len(m.jobs) {
		j := m.jobs[cursor]
		scoreText := fmt.Sprintf("%d%%", j.FitScore)
		if j.FitScore >= 75 {
			scoreText = greenScore.Render(scoreText)
		} else {
			scoreText = yellowScore.Render(scoreText)
		}

		details := fmt.Sprintf(
			"📌 %s (%s)\n🏢 Empresa: %s | 📍 %s (%s)\n⭐ Fit Score: %s — %s\n🏷️  Tags: %s\n🔗 Link: %s",
			j.Title, j.Seniority,
			j.Company, j.Location, j.Modality,
			scoreText, j.FitReason,
			strings.Join(j.Tags, ", "),
			j.URL,
		)
		view += "\n" + detailStyle.Render(details)
	}

	statusHelp := lipgloss.NewStyle().Foreground(lipgloss.Color("241")).Render("\n" + m.msg)
	return view + statusHelp + "\n"
}

func openBrowser(url string) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	case "darwin":
		cmd = exec.Command("open", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}
	_ = cmd.Start()
}

// RunTUI inicializa a interface Bubbletea
func RunTUI(db *storage.DB) error {
	m, err := NewModel(db)
	if err != nil {
		return err
	}
	p := tea.NewProgram(m, tea.WithAltScreen())
	_, err = p.Run()
	return err
}
