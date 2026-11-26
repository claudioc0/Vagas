package fitscore_test

import (
	"testing"
	"vagas-go/internal/domain"
	"vagas-go/pkg/fitscore"
)

func TestEvaluateFreelance(t *testing.T) {
	cases := []struct {
		title  string
		skills []string
		ok     bool
	}{
		{"Claude Chatbot for Product Queries", []string{"Python", "AI Chatbot"}, true},
		{"Senior Golang API", nil, true}, // senioridade não bloqueia freelance
		{"Data Entry with Python", []string{"Python"}, false},
		{"Python homework help", []string{"Python"}, false},
		{"Experienced Developer for BGMI Emulator Hack", []string{"Python"}, false},
		{"Hindi 2D Family Series Animator", []string{"AI"}, false},
		{"India UPI and IMPS Payment Test", []string{"API", "Node.js"}, false},
		{"Fix my WordPress theme, ready to go", []string{"WordPress", "PHP"}, false},
	}
	for _, c := range cases {
		job := domain.Job{Title: c.title, Skills: c.skills, Seniority: domain.SeniorityFreelance, Modality: domain.ModalityRemote}
		score, reason, _ := fitscore.Evaluate(&job)
		if (score >= 50) != c.ok {
			t.Errorf("%q: score %d (%s), esperado aprovado=%v", c.title, score, reason, c.ok)
		}
	}
}
