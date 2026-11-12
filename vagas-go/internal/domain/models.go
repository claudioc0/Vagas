package domain

import (
	"crypto/sha256"
	"fmt"
	"strings"
	"time"
)

// Modality define se a vaga é Remota, Híbrida ou Presencial
type Modality string

const (
	ModalityRemote  Modality = "Remoto"
	ModalityHybrid  Modality = "Híbrido"
	ModalityOnSite  Modality = "Presencial"
	ModalityUnknown Modality = "Indefinido"
)

// Job representa a entidade central de uma oportunidade de emprego
type Job struct {
	ID          string    `json:"id"`           // Hash SHA-256 único
	SourceID    string    `json:"source_id"`    // Ex: "github_frontendbr", "remotar", "gupy"
	Title       string    `json:"title"`
	Company     string    `json:"company"`
	Location    string    `json:"location"`
	Modality    Modality  `json:"modality"`
	Seniority   string    `json:"seniority"`    // Ex: "Júnior", "Trainee"
	URL         string    `json:"url"`
	Description string    `json:"description"`
	Tags        []string  `json:"tags"`
	FitScore    int       `json:"fit_score"`    // 0 a 100
	FitReason   string    `json:"fit_reason"`
	PublishedAt time.Time `json:"published_at"`
	CollectedAt time.Time `json:"collected_at"`
}

// GenerateID calcula um identificador único imutável para a vaga
func (j *Job) GenerateID() string {
	cleanCompany := strings.ToLower(strings.TrimSpace(j.Company))
	cleanTitle := strings.ToLower(strings.TrimSpace(j.Title))
	cleanURL := strings.ToLower(strings.TrimSpace(j.URL))
	
	raw := fmt.Sprintf("%s|%s|%s", cleanCompany, cleanTitle, cleanURL)
	sum := sha256.Sum256([]byte(raw))
	return fmt.Sprintf("%x", sum)
}

// Source representa a origem da coleta
type Source struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Type      string    `json:"type"` // "api", "scraper", "rss", "imap"
	BaseURL   string    `json:"base_url"`
	Active    bool      `json:"active"`
	LastRunAt time.Time `json:"last_run_at"`
}

// ApplicationStatus representa as fases de candidatura
type ApplicationStatus string

const (
	StatusDiscovered ApplicationStatus = "Descoberta"
	StatusCVCreated  ApplicationStatus = "CV Gerado"
	StatusApplied    ApplicationStatus = "Candidatado"
	StatusInterview  ApplicationStatus = "Entrevista"
	StatusRejected   ApplicationStatus = "Rejeitado"
	StatusOffer      ApplicationStatus = "Oferta"
)

// Application registra a candidatura a uma vaga
type Application struct {
	ID          int64             `json:"id"`
	JobID       string            `json:"job_id"`
	Folder      string            `json:"folder"` // Ex: "28_empresa_cargo"
	Status      ApplicationStatus `json:"status"`
	CVPath      string            `json:"cv_path"`
	Notes       string            `json:"notes"`
	UpdatedAt   time.Time         `json:"updated_at"`
}
