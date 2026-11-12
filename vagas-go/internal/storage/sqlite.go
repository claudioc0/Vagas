package storage

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	_ "modernc.org/sqlite"
	"vagas-go/internal/domain"
)

// DB encapsula a conexão SQLite
type DB struct {
	conn *sql.DB
}

// Open inicializa a conexão com o banco SQLite e executa migrações
func Open(dbPath string) (*DB, error) {
	conn, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, fmt.Errorf("falha ao abrir banco sqlite: %w", err)
	}

	conn.SetMaxOpenConns(1)
	conn.SetMaxIdleConns(1)

	db := &DB{conn: conn}
	if err := db.migrate(); err != nil {
		conn.Close()
		return nil, fmt.Errorf("falha ao executar migrações: %w", err)
	}

	return db, nil
}

// Close fecha a conexão com o banco
func (db *DB) Close() error {
	return db.conn.Close()
}

func (db *DB) migrate() error {
	schema := `
	CREATE TABLE IF NOT EXISTS fontes (
		id TEXT PRIMARY KEY,
		nome TEXT NOT NULL,
		tipo TEXT NOT NULL,
		url_base TEXT,
		ativo INTEGER DEFAULT 1,
		ultima_execucao DATETIME
	);

	CREATE TABLE IF NOT EXISTS vagas (
		id TEXT PRIMARY KEY,
		fonte_id TEXT NOT NULL,
		titulo TEXT NOT NULL,
		empresa TEXT NOT NULL,
		localizacao TEXT,
		modalidade TEXT,
		senioridade TEXT,
		link TEXT NOT NULL,
		descricao TEXT,
		tags TEXT,
		fit_score INTEGER DEFAULT 0,
		fit_reason TEXT,
		publicada_em DATETIME,
		coletada_em DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY(fonte_id) REFERENCES fontes(id)
	);

	CREATE TABLE IF NOT EXISTS candidaturas (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		vaga_id TEXT NOT NULL UNIQUE,
		pasta_local TEXT,
		status TEXT NOT NULL,
		cv_path TEXT,
		notas TEXT,
		atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY(vaga_id) REFERENCES vagas(id)
	);

	CREATE TABLE IF NOT EXISTS notificacoes (
		vaga_id TEXT NOT NULL,
		canal TEXT NOT NULL,
		enviado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
		PRIMARY KEY(vaga_id, canal),
		FOREIGN KEY(vaga_id) REFERENCES vagas(id)
	);

	CREATE INDEX IF NOT EXISTS idx_vagas_score ON vagas(fit_score DESC);
	CREATE INDEX IF NOT EXISTS idx_vagas_empresa ON vagas(empresa);
	CREATE INDEX IF NOT EXISTS idx_candidaturas_status ON candidaturas(status);
	`

	_, err := db.conn.Exec(schema)
	return err
}

// UpsertJob insere ou atualiza uma vaga mantendo o histórico de coleta
func (db *DB) UpsertJob(ctx context.Context, job *domain.Job) (bool, error) {
	tagsJSON, _ := json.Marshal(job.Tags)

	query := `
	INSERT INTO vagas (
		id, fonte_id, titulo, empresa, localizacao, modalidade,
		senioridade, link, descricao, tags, fit_score, fit_reason, publicada_em, coletada_em
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	ON CONFLICT(id) DO UPDATE SET
		fit_score = excluded.fit_score,
		fit_reason = excluded.fit_reason,
		tags = excluded.tags
	`

	coletada := job.CollectedAt
	if coletada.IsZero() {
		coletada = time.Now()
	}

	res, err := db.conn.ExecContext(
		ctx,
		query,
		job.ID,
		job.SourceID,
		job.Title,
		job.Company,
		job.Location,
		string(job.Modality),
		job.Seniority,
		job.URL,
		job.Description,
		string(tagsJSON),
		job.FitScore,
		job.FitReason,
		job.PublishedAt,
		coletada,
	)
	if err != nil {
		return false, err
	}

	rows, _ := res.RowsAffected()
	return rows > 0, nil
}

// WasNotified verifica se a vaga já foi notificada em determinado canal
func (db *DB) WasNotified(ctx context.Context, vagaID string, canal string) (bool, error) {
	var count int
	err := db.conn.QueryRowContext(ctx, "SELECT COUNT(*) FROM notificacoes WHERE vaga_id = ? AND canal = ?", vagaID, canal).Scan(&count)
	return count > 0, err
}

// MarkNotified registra envio de notificação
func (db *DB) MarkNotified(ctx context.Context, vagaID string, canal string) error {
	_, err := db.conn.ExecContext(ctx, "INSERT OR IGNORE INTO notificacoes (vaga_id, canal) VALUES (?, ?)", vagaID, canal)
	return err
}

// JobFilter define critérios para consultas
type JobFilter struct {
	MinScore int
	Modality domain.Modality
	Search   string
	Limit    int
}

// ListJobs busca vagas aplicando filtros
func (db *DB) ListJobs(ctx context.Context, filter JobFilter) ([]domain.Job, error) {
	var conditions []string
	var args []interface{}

	if filter.MinScore > 0 {
		conditions = append(conditions, "fit_score >= ?")
		args = append(args, filter.MinScore)
	}

	if filter.Modality != "" && filter.Modality != domain.ModalityUnknown {
		conditions = append(conditions, "modalidade = ?")
		args = append(args, string(filter.Modality))
	}

	if strings.TrimSpace(filter.Search) != "" {
		like := "%" + strings.TrimSpace(filter.Search) + "%"
		conditions = append(conditions, "(titulo LIKE ? OR empresa LIKE ? OR tags LIKE ?)")
		args = append(args, like, like, like)
	}

	whereClause := ""
	if len(conditions) > 0 {
		whereClause = "WHERE " + strings.Join(conditions, " AND ")
	}

	limitClause := ""
	if filter.Limit > 0 {
		limitClause = fmt.Sprintf("LIMIT %d", filter.Limit)
	} else {
		limitClause = "LIMIT 100"
	}

	query := fmt.Sprintf(`
		SELECT id, fonte_id, titulo, empresa, localizacao, modalidade,
		       senioridade, link, descricao, tags, fit_score, fit_reason, publicada_em, coletada_em
		FROM vagas
		%s
		ORDER BY fit_score DESC, coletada_em DESC
		%s
	`, whereClause, limitClause)

	rows, err := db.conn.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var jobs []domain.Job
	for rows.Next() {
		var j domain.Job
		var tagsStr string
		var modStr string

		err := rows.Scan(
			&j.ID,
			&j.SourceID,
			&j.Title,
			&j.Company,
			&j.Location,
			&modStr,
			&j.Seniority,
			&j.URL,
			&j.Description,
			&tagsStr,
			&j.FitScore,
			&j.FitReason,
			&j.PublishedAt,
			&j.CollectedAt,
		)
		if err != nil {
			return nil, err
		}

		j.Modality = domain.Modality(modStr)
		if tagsStr != "" {
			_ = json.Unmarshal([]byte(tagsStr), &j.Tags)
		}
		jobs = append(jobs, j)
	}

	return jobs, nil
}

// CountJobs retorna o total de vagas e a média de score
func (db *DB) CountJobs(ctx context.Context) (total int, elegiveis int, err error) {
	err = db.conn.QueryRowContext(ctx, "SELECT COUNT(*) FROM vagas").Scan(&total)
	if err != nil {
		return 0, 0, err
	}
	err = db.conn.QueryRowContext(ctx, "SELECT COUNT(*) FROM vagas WHERE fit_score >= 60").Scan(&elegiveis)
	return total, elegiveis, err
}
