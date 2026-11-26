package fitscore

import (
	"regexp"
	"strings"
	"vagas-go/internal/domain"
)

// FreelanceReason prefixa o fit_reason de projetos freelance
const FreelanceReason = "Projeto freelance"

var (
	// Trabalhos fora de programação (ou antiéticos, como trabalhos acadêmicos) que as buscas trazem
	reFreelanceExclude = regexp.MustCompile(`(?i)\b(data\s+entry|logo|video\s+edit\w*|translat\w+|content\s+writ\w+|article\s+writ\w+|copywrit\w+|seo|marketing|telemarketing|virtual\s+assistant|lead\s+generation|cold\s+call\w*|sales|graphic\s+design|illustrat\w+|homework|assignment|thesis|dissertation|research|video\w*|animat\w+|music|track|audio|voice|speakers?|recording|annotat\w+|labell?ing|collect|collection|partner|hack\w*|cheat\w*|aimbot|betting|casino|gambling|payment\s+test\w*)\b`)

	// "go" isolado é palavra comum em inglês, por isso só "golang"
	freelanceAreas = []struct {
		Pattern *regexp.Regexp
		Points  int
		Tag     string
	}{
		{regexp.MustCompile(`(?i)\b(ai|llms?|gpt|openai|claude|gemini|genai|rag|langchain|machine\s+learning|artificial\s+intelligence|ia)\b`), 15, "IA/LLM"},
		{regexp.MustCompile(`(?i)\b(chat\s*bots?|ai\s+agents?|agentic)\b`), 10, "Chatbot/Agentes"},
		{regexp.MustCompile(`(?i)\b(automation|automa[cç][aã]o|n8n|web\s*scraping|scraper)\b`), 10, "Automação"},
		{regexp.MustCompile(`(?i)\bpython\b`), 15, "Python"},
		{regexp.MustCompile(`(?i)\bgolang\b`), 15, "Go"},
		{regexp.MustCompile(`(?i)\b(react(\.?js)?|next\.?js)\b`), 10, "React"},
		{regexp.MustCompile(`(?i)\b(node(\.?js)?|typescript)\b`), 10, "Node/TS"},
		{regexp.MustCompile(`(?i)\b(data\s+(analysis|analytics|engineering|science)|sql|power\s*bi|etl)\b`), 10, "Dados"},
	}
)

// evaluateFreelance pontua projetos: não há nível Júnior, importam a área e a concorrência.
// A área é buscada no título e nas skills; a descrição gera ruído demais.
func evaluateFreelance(job *domain.Job) (int, string, []string) {
	if reFreelanceExclude.MatchString(job.Title) {
		return 0, "Projeto fora da área de programação", nil
	}

	text := job.Title + " | " + strings.Join(job.Skills, " | ")
	score := 45
	var tags []string
	for _, area := range freelanceAreas {
		if area.Pattern.MatchString(text) {
			score += area.Points
			tags = append(tags, area.Tag)
		}
	}
	if len(tags) == 0 {
		return 0, "Projeto sem relação com as áreas de interesse", nil
	}

	// Bônus por baixa concorrência
	switch {
	case job.Bids <= 10:
		score += 10
	case job.Bids <= 20:
		score += 5
	}
	if score > 100 {
		score = 100
	}
	return score, FreelanceReason + " (" + strings.Join(tags, ", ") + ")", tags
}
