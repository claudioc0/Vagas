package provider

import (
	"testing"
	"time"
)

func TestFreelancerAccepted(t *testing.T) {
	now := time.Now()
	base := freelancerProject{SEOURL: "a/b", Status: "active", Language: "en", Type: "fixed", Submitted: now.Add(-time.Hour).Unix()}
	base.Budget.Minimum, base.Budget.Maximum = 250, 750
	base.Currency.ExchangeRate = 1
	base.BidStats.BidCount = 30

	if !base.accepted(now) {
		t.Fatal("projeto base deveria ser aceito")
	}
	reject := map[string]func(p *freelancerProject){
		"muitas propostas": func(p *freelancerProject) { p.BidStats.BidCount = 31 },
		"antigo":           func(p *freelancerProject) { p.Submitted = now.Add(-25 * time.Hour).Unix() },
		"espanhol":         func(p *freelancerProject) { p.Language = "es" },
		"barato em USD":    func(p *freelancerProject) { p.Currency.ExchangeRate = 0.012 },
		"hora barata": func(p *freelancerProject) {
			p.Type = "hourly"
			p.Budget.Minimum, p.Budget.Maximum = 8, 14
		},
	}
	for name, mutate := range reject {
		p := base
		mutate(&p)
		if p.accepted(now) {
			t.Errorf("%s: deveria ser rejeitado", name)
		}
	}
}
