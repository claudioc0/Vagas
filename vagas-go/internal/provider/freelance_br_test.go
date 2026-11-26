package provider

import (
	"fmt"
	"testing"
	"time"
)

func TestParse99Freelas(t *testing.T) {
	now := time.Now()
	card := func(id int, category string, age time.Duration, bids int) string {
		return fmt.Sprintf(`<li class="with-flag result-item" data-id="%d">
<h1 class="title"> <a href="/project/projeto-%d?fs=t">Automa&ccedil;&atilde;o com Python</a> </h1>
<p class="item-text information"> %s | Iniciante | Publicado: <b class="datetime" cp-datetime="%d"></b> | Propostas: <b>%d</b> </p>
<div class="item-text description formatted-text" data-content="x"> Descri&ccedil;&atilde;o </div>
<p class="item-text habilidades"> <a class="habilidade">Python</a> </p></li>`, id, id, category, now.Add(-age).UnixMilli(), bids)
	}
	body := card(1, "Desenvolvimento Web", time.Hour, 5) +
		card(2, "Desenvolvimento Web", time.Hour, 31) +
		card(3, "Desenvolvimento Web", 30*time.Hour, 5) +
		card(4, "UX/UI &amp; Web Design", time.Hour, 5)

	jobs, parsed := parse99Freelas(body, now)
	if parsed != 4 || len(jobs) != 1 {
		t.Fatalf("esperava 4 lidos e 1 aprovado, obteve %d e %d", parsed, len(jobs))
	}
	j := jobs[0]
	if j.Title != "Automação com Python" || j.URL != "https://www.99freelas.com.br/project/projeto-1" ||
		len(j.Skills) != 1 || j.Description != "Descrição" {
		t.Errorf("campos inesperados: %+v", j)
	}
}

func TestParseWorkana(t *testing.T) {
	body := `<search :results-initials='{&quot;results&quot;:[
{"slug":"a","title":"<span title=\"Chatbot com IA\">Chatbot...</span>","postedDate":"há 14 minutos","budget":"USD 100 - 250","totalBids":"Propostas: 14"},
{"slug":"b","title":"x","postedDate":"Ontem","budget":"USD 100 - 250","totalBids":"Propostas: 1"},
{"slug":"c","title":"x","postedDate":"Agora mesmo","budget":"USD 50 - 100","totalBids":"Propostas: 1"},
{"slug":"d","title":"x","postedDate":"Agora mesmo","budget":"USD 500 - 1.000","totalBids":"Propostas: 51"}]}'>`

	jobs, err := parseWorkana(body, time.Now())
	if err != nil {
		t.Fatal(err)
	}
	if len(jobs) != 1 || jobs[0].Title != "Chatbot com IA" || jobs[0].URL != "https://www.workana.com/job/a" {
		t.Fatalf("resultado inesperado: %+v", jobs)
	}
	if _, err := parseWorkana("<html></html>", time.Now()); err == nil {
		t.Error("página sem dados deveria retornar erro")
	}
}

func TestWorkanaBudget(t *testing.T) {
	for budget, want := range map[string]bool{
		"USD 500 - 1.000": true, "USD 50 - 100": false, "Mais de USD 3.000": true, "Menos de USD 50": false,
	} {
		if got := workanaBudgetOK(budget, false); got != want {
			t.Errorf("%q: obteve %v", budget, got)
		}
	}
}
