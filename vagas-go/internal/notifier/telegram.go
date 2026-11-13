package notifier

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"
	"vagas-go/internal/domain"
	"vagas-go/internal/storage"
)

type TelegramNotifier struct {
	token  string
	chatID string
	client *http.Client
	db     *storage.DB
}

func NewTelegramNotifier(db *storage.DB) *TelegramNotifier {
	return &TelegramNotifier{
		token:  os.Getenv("TELEGRAM_BOT_TOKEN"),
		chatID: os.Getenv("TELEGRAM_CHAT_ID"),
		client: &http.Client{Timeout: 10 * time.Second},
		db:     db,
	}
}

func (t *TelegramNotifier) IsConfigured() bool {
	return t.token != "" && t.chatID != ""
}

// NotifyHotJobs envia alertas para vagas com fit_score >= minScore que ainda não foram enviadas
func (t *TelegramNotifier) NotifyHotJobs(ctx context.Context, jobs []domain.Job, minScore int) (int, error) {
	if !t.IsConfigured() {
		return 0, nil
	}

	var toNotify []domain.Job
	for _, j := range jobs {
		if j.FitScore < minScore {
			continue
		}
		wasSent, err := t.db.WasNotified(ctx, j.ID, "telegram")
		if err != nil || wasSent {
			continue
		}
		toNotify = append(toNotify, j)
	}

	if len(toNotify) == 0 {
		return 0, nil
	}

	sentCount := 0
	for _, j := range toNotify {
		tags := strings.Join(j.Tags, " • ")
		if tags == "" {
			tags = "Geral"
		}

		msg := fmt.Sprintf(
			"🎯 <b>NOVA VAGA QUENTE (Fit %d%%)</b>\n\n"+
				"📌 <b>%s</b>\n"+
				"🏢 Empresa: <b>%s</b>\n"+
				"📍 Modalidade: %s\n"+
				"🏷️ Tags: <code>%s</code>\n\n"+
				"🔗 <a href=\"%s\">Acessar e Candidatar-se</a>",
			j.FitScore,
			escapeHTML(j.Title),
			escapeHTML(j.Company),
			j.Modality,
			escapeHTML(tags),
			j.URL,
		)

		if err := t.sendMessage(ctx, msg); err != nil {
			fmt.Printf("  [Telegram] Erro ao enviar vaga %s: %v\n", j.ID, err)
			continue
		}

		_ = t.db.MarkNotified(ctx, j.ID, "telegram")
		sentCount++
		time.Sleep(300 * time.Millisecond) // Respeitar rate-limit do Telegram
	}

	return sentCount, nil
}

// NotifyScanSummary envia um resumo de execução quando nenhuma vaga nova é notificada
func (t *TelegramNotifier) NotifyScanSummary(ctx context.Context, totalUnique, eligible, highFit, minScore int) error {
	if !t.IsConfigured() {
		return nil
	}

	msg := fmt.Sprintf(
		"🔎 <b>Radar de Vagas executado</b>\n\n"+
			"• Vagas únicas varridas: %d\n"+
			"• Elegíveis (Score ≥50): %d\n"+
			"• Alto Fit (Score ≥75): %d\n"+
			"• Novas enviadas: 0\n\n"+
			"<i>Nenhuma vaga nova pendente com Score ≥%d.</i>",
		totalUnique,
		eligible,
		highFit,
		minScore,
	)

	return t.sendMessage(ctx, msg)
}

func (t *TelegramNotifier) sendMessage(ctx context.Context, text string) error {
	apiURL := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", t.token)
	payload := map[string]any{
		"chat_id":                  t.chatID,
		"text":                     text,
		"parse_mode":               "HTML",
		"disable_web_page_preview": true,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, apiURL, bytes.NewBuffer(body))
	if err != nil {
		return err
	}
	req.Method = http.MethodPost
	req.Header.Set("Content-Type", "application/json")

	resp, err := t.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("telegram status code: %d", resp.StatusCode)
	}
	return nil
}

func escapeHTML(s string) string {
	s = strings.ReplaceAll(s, "&", "&amp;")
	s = strings.ReplaceAll(s, "<", "&lt;")
	s = strings.ReplaceAll(s, ">", "&gt;")
	return s
}
