package fitscore

import (
	"regexp"
	"strings"
	"vagas-go/internal/domain"
)

var (
	reSeniorityDisqualify = regexp.MustCompile(`(?i)\b(pleno|pl|mid|mid-level|s[eê]nior|sr|sr\.|lead|staff|principal|especialista|master|head|gerente|diretor|coordenador(a)?)\b`)
	reJuniorExplicit      = regexp.MustCompile(`(?i)\b(j[uú]nior|jr\b|jr\.|trainee|entry(\s+level)?)\b`)
	reInternship          = regexp.MustCompile(`(?i)\b(est[aá]gio|estagi[aá]ri[oa]|internship|intern\b)\b`)
	reTrainee             = regexp.MustCompile(`(?i)\btrainee\b`)

	reAffirmative = regexp.MustCompile(`(?i)(\bpcd\b|\(pcd\)|\[pcd\]|-pcd-|_pcd_|exclusiv[ao]\s+para\s+mulheres|afirmativ[ao]\s+para\s+mulheres|para\s+pessoas?\s+com\s+defici[eê]ncia|exclusiv[ao]\s+(pcd|para\s+pcd))`)

	reNonCoreTech = regexp.MustCompile(`(?i)\b(opera[cç][oõ]es|operacional|medi[cç][aã]o|faturamento|setor\s+el[eé]trico|el[eé]tric[ao]|eletrot[eé]cnic[ao]|smf|suporte|help\s*desk|service\s*desk|atendimento|infraestrutura|redes|telecom|t[eé]cnic[ao]\s+de\s+ti|t[eé]cnic[ao]\s+de\s+inform[aá]tica|processos|melhoria\s+cont[ií]nua|pcm|manuten[cç][aã]o|facilities|marketing|seo|m[ií]dia|growth|tr[aá]fego|web\s+analytics|comercial|vendas|designer?|ui/ux|ux/ui|controladoria|cont[aá]bil|fiscal|recrutamento|professor|professora|ingl[eê]s|qu[ií]mica|farm[aá]cia)\b`)

	reCoreTech = regexp.MustCompile(`(?i)\b(dev|desenvolvedor(a)?|developer|software|programador(a)?|engenheiro(a)?\s+de\s+software|engenharia\s+de\s+software|full\s*stack|front\s*end|frontend|back\s*end|backend|mobile|web|intelig[eê]ncia\s+artificial|\bia\b|ai\b|genai|llm|machine\s+learning|prompt|dados|data\s+engineer|engenheir[oa]\s+de\s+dados|cientista\s+de\s+dados|analista\s+de\s+dados|power\s*bi|qa|qualidade\s+de\s+software|testes?|test\s+engineer|ciberseguran[cç]a|cybersecurity|pentest(er)?|seguran[cç]a\s+da\s+informa[cç][aã]o|appsec|rpa|automa[cç][aã]o\s+de\s+software|python|golang|go|java|react|typescript|node)\b`)

	techKeywords = []struct {
		Pattern *regexp.Regexp
		Points  int
		Tag     string
	}{
		{regexp.MustCompile(`(?i)\b(golang|go)\b`), 15, "Go"},
		{regexp.MustCompile(`(?i)\b(python)\b`), 15, "Python"},
		{regexp.MustCompile(`(?i)\b(react|reactjs|next|nextjs)\b`), 10, "React"},
		{regexp.MustCompile(`(?i)\b(typescript|ts)\b`), 10, "TypeScript"},
		{regexp.MustCompile(`(?i)\b(node|nodejs)\b`), 10, "Node.js"},
		{regexp.MustCompile(`(?i)\b(sql|postgres|sqlite|mysql)\b`), 10, "SQL"},
		{regexp.MustCompile(`(?i)\b(docker|containers?)\b`), 5, "Docker"},
		{regexp.MustCompile(`(?i)\b(ia|ai|llm|genai|rag|langchain)\b`), 15, "IA/LLM"},
		{regexp.MustCompile(`(?i)\b(git|github)\b`), 5, "Git"},
	}
)

// Evaluate calcula o FitScore (0 a 100) e a justificativa para uma vaga
func Evaluate(job *domain.Job) (int, string, []string) {
	title := job.Title
	desc := job.Description
	loc := strings.ToLower(job.Location)
	fullText := strings.ToLower(title + " " + job.Company + " " + desc + " " + job.URL)

	// 1. Desqualificador de Senioridade
	if reSeniorityDisqualify.MatchString(title) {
		return 0, "Nível acima de Júnior (Pleno/Sênior/Lead/Especialista)", nil
	}

	// 2. Exigência de ser Júnior ou Trainee
	isJr := reJuniorExplicit.MatchString(title) || reJuniorExplicit.MatchString(desc)
	if !isJr {
		return 0, "Não é vaga explicitamente Júnior ou Trainee", nil
	}

	// 3. Bloqueio de Estágio (Formando 12/2026)
	if reInternship.MatchString(title) && !reTrainee.MatchString(title) {
		return 0, "Vaga de estágio (não elegível)", nil
	}

	// 4. Bloqueio de vagas afirmativas exclusivas
	if reAffirmative.MatchString(fullText) {
		return 0, "Vaga afirmativa ou exclusiva para grupos específicos", nil
	}

	// 5. Bloqueio de áreas não-core dev
	if reNonCoreTech.MatchString(title) {
		return 0, "Área não-core dev/tech (operações/suporte/elétrico/administrativo)", nil
	}

	// 6. Confirmação de ser Core Tech
	if !reCoreTech.MatchString(title) {
		return 0, "Título não corresponde a Core Tech/Software/Dados", nil
	}

	// 7. Compatibilidade de Localização (Se presencial/híbrido, deve ser Curitiba/PR)
	if job.Modality == domain.ModalityOnSite || job.Modality == domain.ModalityHybrid {
		isCuritiba := strings.Contains(loc, "curitiba") || strings.Contains(loc, "pinhais") ||
			strings.Contains(loc, "são josé dos pinhais") || strings.Contains(loc, "colombo") ||
			strings.Contains(loc, "araucária") || strings.Contains(loc, "paraná") || strings.Contains(loc, "pr")
		if !isCuritiba && (strings.Contains(loc, "são paulo") || strings.Contains(loc, "sp") ||
			strings.Contains(loc, "rio de janeiro") || strings.Contains(loc, "rj") ||
			strings.Contains(loc, "belo horizonte") || strings.Contains(loc, "bh") ||
			strings.Contains(loc, "porto alegre")) {
			return 0, "Vaga presencial/híbrida fora do polo Curitiba/PR", nil
		}
	}

	// Cálculo de Pontuação (Score positivo)
	score := 50 // Base de elegibilidade estrita aprovada
	var tags []string

	for _, kw := range techKeywords {
		if kw.Pattern.MatchString(fullText) {
			score += kw.Points
			tags = append(tags, kw.Tag)
		}
	}

	// Bônus de modalidade
	if job.Modality == domain.ModalityRemote {
		score += 10
	} else if strings.Contains(loc, "curitiba") {
		score += 5
	}

	// Bônus se tiver "Júnior" explícito no título
	if reJuniorExplicit.MatchString(title) {
		score += 10
	}

	if score > 100 {
		score = 100
	}

	reason := "Elegível Júnior Tech"
	if len(tags) > 0 {
		reason += " (" + strings.Join(tags, ", ") + ")"
	}

	return score, reason, tags
}
