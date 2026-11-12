"""Conteúdo adaptado por vaga. Fatos extraídos de 'Contexto para Candidaturas'."""

EXTRAS_BASE = [
    "Estágio em Análise de Dados (Power BI) – Oregon Tool – 2026",
    "Cisco Networking Academy: Python (2023), Segurança de Endpoint (2024), Analista de Cibersegurança Júnior (2026), Data Science, Prompt Engineering Essentials",
    "Extensão PUCPR/Copel: mapeamento de processos (MPS.BR), gap analysis e proposta de automações",
]

P_PERFORA = ("Perfora – SaaS com IA generativa", "Flask, React Native/Expo, Gemini API, SQLite, Azure DevOps, SonarCloud",
             "App de rastreamento nutricional que estima calorias e macros a partir de fotos. Backend REST em camadas com JWT, hash de senha e rate limiting; suíte pytest; pipeline CI/CD com quality gate no SonarCloud. Desenvolvido sozinho, de ponta a ponta.")
P_TRADING = ("Simulador de Trading", "React, TypeScript, Node.js, SQLite",
             "Site educacional de trading simulado (ações, cripto, memecoins) para iniciantes, sem dinheiro real: interfaces de carteira, ordens e cotações consumindo API própria.")
P_CLEARBOX = ("ClearBox – classificador de e-mails", "IA / LLM",
              "Classifica e-mails em produtivos/improdutivos, sugere resposta e exibe percentual de confiabilidade.")
P_EDITOR = ("EditorLeads – MicroSaaS", "GPT-4o-mini, Cursor",
            "Ferramenta de prospecção para editores de vídeo com algoritmo de Fit Score; construída com desenvolvimento assistido por IA, com 30 testes unitários e 94% de cobertura.")
P_XADREZ = ("Jogo de xadrez com modo carreira", "Godot Engine (GDScript)",
            "Jogo desktop em pixel art com regras ortodoxas e modo carreira narrativo próprio.")
P_GLOBAL = ("GlobalStable", "AWS, Docker",
            "Conversão de moedas fiduciárias para stablecoins; ambientes conteinerizados e pipelines de teste na AWS.")
P_CEP = ("Biblioteca de Controle Estatístico de Processos", "Python, Jupyter",
         "Implementação própria de gráficos de controle (XbarR, XbarS, XmR, XMmR) para análise estatística de dados.")
P_CODEREVI = ("CodeRevi", "Node.js",
              "App gamificado de revisão de código com XP, badges, leaderboard e integração com Discord.")

VAGAS = {
    "01_doc9_dev_vibecode": {
        "titulo": "Desenvolvedor Júnior · IA",
        "skills": [("Desenvolvimento com IA", "Claude Code, Cursor, ChatGPT, prompt engineering"),
                   ("Web", "React, TypeScript, HTML/CSS/JS, Node.js, Flask"),
                   ("Dados", "SQL/MySQL, SQLite, modelagem relacional"),
                   ("Qualidade e segurança", "pytest, TDD, JWT, bcrypt, prevenção de SQL injection"),
                   ("Ferramentas", "Git/GitHub, Docker, Azure DevOps")],
        "objetivo": "Atuar como Dev Vibecode na doc9, criando e refinando protótipos com plataformas de Vibe Coding, escrevendo instruções claras para guiar a IA na geração de código e testando fluxos de aplicação com atenção a usabilidade e segurança de dados.",
        "resumo": "Estudante de Engenharia de Software (8º período, PUCPR) que já usa IA generativa como parte central do fluxo de desenvolvimento: construí produtos completos com Claude Code e Cursor, sempre validando criticamente o código gerado com testes automatizados. Tenho base sólida em lógica, web (frontend e backend) e bancos relacionais, certificação em Prompt Engineering e cuidado com segurança (autenticação, hash de senhas, LGPD).",
        "projetos": [P_EDITOR, P_PERFORA, P_CLEARBOX, P_TRADING],
        "extras": EXTRAS_BASE + ["Projeto acadêmico de Segurança de Software (Python/MVC): bcrypt, prevenção de SQL injection, bloqueio de conta e log de auditoria"],
        "respostas": """
# doc9 – Dev Vibecode (remoto, CLT, 8h30–18h18)
Link: https://safehire.doc9hub.com/vagas/986dad70-18dd-4384-a701-bcb0ac1b173c

- Nome: Claudio Colombo Ferreira
- Email: claudiocolomboferreira13@gmail.com
- Telefone: +55 41 98811-5804
- LinkedIn: https://www.linkedin.com/in/claudio-colombo-ferreira
- País: Brasil · Estado/cidade: Paraná / Pinhais
- Currículo: Curriculo_Claudio_Colombo.pdf (nesta pasta)
- Pretensão salarial: R$ 3.000 a R$ 4.000 (negociável conforme benefícios)
- Indicação: Não
- LGPD: marcar

ATENÇÃO: o horário é integral (8h30–18h18). Confirme se é compatível com suas aulas do 8º período antes de enviar.
""",
    },
    "02_deepesg_desenvolvedor": {
        "titulo": "Desenvolvedor · Protótipos e Dados",
        "skills": [("Linguagens", "Python (avançado), TypeScript, Java, C#, SQL"),
                   ("Dados e IA", "Data Science (Cisco), Power BI, LLMs (Gemini, GPT), estatística aplicada"),
                   ("Prototipagem", "Flask, React, React Native, Node.js, Godot"),
                   ("Engenharia", "pytest, JUnit, mutation testing, CI/CD, Docker, AWS")],
        "objetivo": "Fazer parte do time de tecnologia e inovação da DEEP ESG construindo protótipos e provas de conceito, transformando hipóteses em soluções funcionais com dados, algoritmos e automações aplicados à sustentabilidade.",
        "resumo": "Sou um perfil \"fazedor\": ao longo da graduação em Engenharia de Software (PUCPR, conclusão 12/2026) construí por conta própria mais de sete projetos completos, de um SaaS com IA de visão a um jogo em Godot e uma biblioteca estatística em Python. Tenho veia de pesquisa: meu TCC compara empiricamente qualidade de testes em monólitos e microsserviços com métricas como mutation score. Aprendo stacks novas rápido e gosto de validar ideias com experimentos.",
        "projetos": [P_PERFORA, P_CEP, P_CLEARBOX, P_GLOBAL, P_XADREZ],
        "extras": EXTRAS_BASE + ["Pesquisa (TCC): estudo comparativo de cobertura, conformidade arquitetural (ArchUnit) e mutation score (Pitest) entre arquiteturas"],
        "respostas": """
# DEEP ESG – Desenvolvedor (remoto)
Link: https://deepesg.inhire.app/vagas/7c4188a2-79af-4650-a814-2edbe70fe00d/desenvolvedor

Campos obrigatórios: LinkedIn, pretensão salarial, currículo.
- LinkedIn: https://www.linkedin.com/in/claudio-colombo-ferreira
- Pretensão: R$ 3.500 a R$ 4.500 CLT (ou R$ 4.500 a R$ 6.000 PJ), negociável
  (nível da vaga não informado; ajuste se pedirem algo mais sênior)
- Currículo: Curriculo_Claudio_Colombo.pdf

Se houver campo de mensagem:
"O que mais me atraiu foi o pedido de 'quero conhecer o que você já construiu'. Construí sozinho o Perfora (estimativa nutricional por foto com Gemini, backend Flask com testes e CI/CD), uma biblioteca de controle estatístico em Python e um classificador de e-mails com IA, além de um TCC empírico sobre qualidade de testes. Aplicar esse jeito de prototipar e experimentar em problemas de impacto socioambiental é exatamente o tipo de desafio que procuro. Portfólio: github.com/claudioc0"
""",
    },
    "03_fullstack_jr_ia_paggins": {
        "titulo": "Desenvolvedor Full Stack Júnior · IA",
        "skills": [("Backend", "Python/Flask, Node.js, ASP.NET Core, APIs REST, JWT"),
                   ("Frontend", "React, TypeScript, React Native/Expo"),
                   ("IA aplicada", "Gemini API, GPT-4o-mini, Claude Code, Cursor, prompt engineering"),
                   ("Dados", "SQL/MySQL, SQLite"),
                   ("Qualidade", "pytest, TDD, SonarCloud, CI/CD Azure DevOps")],
        "objetivo": "Atuar como Desenvolvedor Full Stack Júnior construindo e mantendo sistemas com IA integrada no dia a dia, programando com Claude/Codex e entregando funcionalidades reais baseadas em modelos de linguagem.",
        "resumo": "Estudante de Engenharia de Software (8º período, PUCPR) que já entrega funcionalidades reais com LLMs: integrei a Gemini API a um backend Flask para análise de imagens, construí um classificador de e-mails com IA e um MicroSaaS sobre GPT-4o-mini. Programo diariamente com Claude Code, revisando e testando o que a IA gera (94% de cobertura no EditorLeads). Experiência full stack com React/TypeScript no front e APIs REST seguras no back.",
        "projetos": [P_PERFORA, P_CLEARBOX, P_EDITOR, P_TRADING],
        "extras": EXTRAS_BASE,
        "respostas": """
# Full Stack Jr com foco em IA (Paggins / SIP / HYU) – Google Forms
Link: https://docs.google.com/forms/d/e/1FAIpQLSf7rReVzvdm4B66scbEZWo8IudTzPR2gQdYBVXpt1g-yRaM_g/viewform

1. Nome completo: Claudio Colombo Ferreira
2. WhatsApp: (41) 98811-5804
3. Cidade e estado: Pinhais – PR (região de Curitiba)
4. GitHub ou portfólio:
   https://github.com/claudioc0 – destaque para o Perfora: backend Flask em camadas (JWT, rate limiting, pytest, CI/CD Azure DevOps + SonarCloud) integrado à Gemini API para estimar calorias por foto, com app React Native. Também ClearBox (classificação de e-mails com IA + sugestão de resposta) e EditorLeads (MicroSaaS com GPT-4o-mini, 94% de cobertura). Uso Claude Code diariamente, sempre revisando e testando o código gerado.
   >> Confira se esses repositórios estão públicos antes de enviar.
5. Pretensão: R$ 3.000 a R$ 4.000 (CLT) ou R$ 4.000 a R$ 6.000 (PJ), negociável
6. Início: "Até 15 dias" (ou "Imediato", se você puder)

O formulário não pede currículo; mande o PDF desta pasta se entrarem em contato.
""",
    },
    "04_jungle_gaming_frontend": {
        "titulo": "Desenvolvedor Front-end Júnior",
        "skills": [("Frontend", "React, TypeScript, JavaScript, HTML5, CSS3, React Native/Expo, Angular"),
                   ("Dados e APIs", "Consumo de APIs REST, estados assíncronos (loading/erro/vazio), Node.js"),
                   ("Qualidade", "Componentização, testes automatizados, CI/CD, SonarCloud"),
                   ("Fluxo", "Git/GitHub, ferramentas de IA agêntica (Claude Code, Cursor)"),
                   ("Games", "Godot Engine (GDScript)")],
        "objetivo": "Atuar como Junior Frontend Developer na Jungle Gaming, transformando designs em interfaces React/TypeScript rápidas, responsivas e reutilizáveis, e evoluindo em TanStack, Socket.IO e Tailwind com feedback próximo de design e engenharia.",
        "resumo": "Estudante de Engenharia de Software (8º período, PUCPR) com React e TypeScript demonstrados em projetos: um simulador de trading com cotações, carteira e ordens consumindo API própria, e um app React Native integrado a um backend REST. Cuido dos estados de carregamento, erro e vazio, de componentes reutilizáveis e da responsividade. Gosto de games (desenvolvi um jogo de xadrez em Godot) e uso IA agêntica no dia a dia validando criticamente o que ela gera. Inglês avançado.",
        "projetos": [P_TRADING, P_PERFORA, P_XADREZ, P_CODEREVI],
        "extras": EXTRAS_BASE[:2],
        "respostas": """
# Jungle Gaming – Desenvolvedor Front-end Júnior (remoto, R$ 2.500–5.000)
Candidatura via LinkedIn: https://www.linkedin.com/jobs/view/4472152944
(fonte: stackvagas.dev/vagas?id=6022d4e8-7460-4963-bb96-66b03cff122f)

- Currículo: Curriculo_Claudio_Colombo.pdf
- A vaga pede portfólio/GitHub: https://github.com/claudioc0
  >> Fixe o Simulador de Trading (React+TS) no topo do GitHub; se tiver deploy, inclua o link.
- Pretensão (se perguntada): R$ 4.000
- Inglês: avançado

Mensagem/nota (opcional):
"Olá! Me candidatei à vaga de Junior Frontend Developer. Construí um simulador de trading em React + TypeScript (cotações, carteira, ordens, estados de loading/erro) e um jogo de xadrez em Godot, então juntar frontend e games me anima bastante. Estou terminando Engenharia de Software na PUCPR e uso IA agêntica no fluxo, sempre revisando o que ela gera. Meu GitHub: github.com/claudioc0"
""",
    },
}


# ---- Textos para o modelo PPTX original (tamanhos próximos aos originais para não estourar as caixas) ----
PERFORA = ("Desenvolvimento de Plataforma SaaS (Perfora) Integrada à Inteligência Artificial - Conclusão: 2026",
           "Implementação full-stack de uma aplicação client-server: backend Flask em camadas com APIs RESTful, autenticação JWT, hash de senha e rate limiting, app em React Native e integração com IA Generativa (Gemini API) para analisar imagens e retornar dados estruturados (JSON). Suíte de testes pytest e pipeline CI/CD (Azure DevOps + SonarCloud).")

TEXTOS = {
    "01_doc9_dev_vibecode": dict(
        objetivo="Atuar como Dev Vibecode na doc9, criando e refinando protótipos com ferramentas de Vibe Coding, escrevendo instruções claras e detalhadas para guiar a IA na geração de código, testando fluxos de aplicação e identificando problemas de usabilidade, sempre com atenção à segurança e proteção de dados.",
        resumo="Estudante de Engenharia de Software (8º Período) que já utiliza IA generativa como parte central do desenvolvimento: construí produtos completos com Claude Code e Cursor, revisando criticamente o código gerado e validando-o com testes automatizados. Tenho base sólida em lógica de programação, web (frontend e backend) e bancos de dados relacionais, certificação em Prompt Engineering e cuidado com segurança da informação e LGPD, além de comunicação escrita clara para descrever problemas.",
        projetos=[PERFORA,
                  ("EditorLeads – MicroSaaS desenvolvido com IA (Vibe Coding) - Conclusão: 2026",
                   "Ferramenta de prospecção de clientes para editores de vídeo freelancer, construída com Cursor e GPT-4o-mini a partir de prompts detalhados, com algoritmo de Fit Score. Validação do código gerado por IA com 30 testes unitários e 94% de cobertura.")],
        skill_cs=("IA Generativa / Prompts", "Intermediário"),
    ),
    "02_deepesg_desenvolvedor": dict(
        objetivo="Fazer parte do time de tecnologia e inovação da DEEP ESG desenvolvendo protótipos e provas de conceito, transformando hipóteses em soluções funcionais com dados, algoritmos e automações, e contribuindo com pesquisa e desenvolvimento de novas aplicações de tecnologia para ESG e sustentabilidade.",
        resumo="Estudante de Engenharia de Software (8º Período) com perfil curioso e mão na massa: construí por conta própria diversos projetos completos, de um SaaS com IA de visão computacional a uma biblioteca estatística em Python e um jogo em Godot. Tenho experiência de pesquisa no TCC, um estudo empírico que compara qualidade de testes entre monólitos e microsserviços usando métricas como mutation score. Aprendo tecnologias novas rapidamente e gosto de validar ideias com experimentos e protótipos.",
        projetos=[PERFORA,
                  ("Biblioteca de Controle Estatístico de Processos em Python - Conclusão: 2025",
                   "Implementação própria, em Python/Jupyter, de gráficos de controle estatístico (XbarR, XbarS, XmR e XMmR) para análise de dados de processos, incluindo cálculo de limites de controle e identificação de pontos fora de controle, com foco em decisões baseadas em dados.")],
        skill_cs=("Python / Dados", "Intermediário"),
    ),
    "03_fullstack_jr_ia_paggins": dict(
        objetivo="Atuar como Desenvolvedor(a) Full Stack Júnior com foco em IA, construindo e mantendo sistemas em que a IA faz parte do dia a dia, programando com Claude e Codex e entregando funcionalidades reais baseadas em modelos de linguagem, com código revisado, testado e pronto para produção.",
        resumo="Estudante de Engenharia de Software (8º Período) que já entrega funcionalidades reais com modelos de linguagem: integrei a Gemini API a um backend Flask para análise de imagens, desenvolvi um classificador de e-mails com IA e um MicroSaaS sobre GPT-4o-mini. Programo diariamente com Claude Code, revisando e testando o que a IA gera. Tenho experiência full-stack com React/TypeScript no frontend, APIs REST seguras no backend, bancos relacionais e Git.",
        projetos=[PERFORA,
                  ("ClearBox – Classificador Inteligente de E-mails com IA - Conclusão: 2026",
                   "Aplicação que utiliza modelos de linguagem para classificar e-mails como produtivos ou improdutivos, sugerir automaticamente uma resposta adequada e exibir o percentual de confiabilidade da classificação, automatizando a triagem de mensagens.")],
        skill_cs=("Python / Flask", "Intermediário"),
    ),
    "04_jungle_gaming_frontend": dict(
        objetivo="Atuar como Desenvolvedor Front-end Júnior na Jungle Gaming, transformando designs e ideias de produto em interfaces React e TypeScript rápidas, responsivas e bem-acabadas, construindo componentes reutilizáveis e evoluindo em TanStack, Socket.IO e Tailwind com feedback próximo de design e engenharia.",
        resumo="Estudante de Engenharia de Software (8º Período) com React e TypeScript demonstrados em projetos: um simulador de trading com cotações, carteira e ordens consumindo API própria, e um app React Native integrado a um backend REST. Tenho atenção aos estados de carregamento, erro e vazio, à componentização e à responsividade. Sou apaixonado por jogos (desenvolvi um xadrez em Godot) e uso ferramentas de IA agêntica no dia a dia, validando criticamente o código gerado.",
        projetos=[("Simulador de Trading Educacional (React + TypeScript) - Conclusão: 2026",
                   "Site educacional de trading simulado (ações, cripto e memecoins) para iniciantes, sem dinheiro real. Frontend em React e TypeScript com telas de cotações, carteira e ordens, consumindo uma API REST própria em Node.js/SQLite e tratando estados de carregamento, erro e dados vazios."),
                  ("Jogo de Xadrez com Modo Carreira (Godot Engine) - Conclusão: 2025",
                   "Jogo desktop de xadrez em pixel art com regras ortodoxas e modo carreira narrativo próprio, desenvolvido em GDScript, com foco em interface clara, feedback visual das jogadas e experiência do jogador.")],
        skill_cs=("React / TypeScript", "Intermediário"),
    ),
}
for _k, _t in TEXTOS.items():
    VAGAS[_k].update(_t)


from vagas_busca1 import NOVAS  # noqa: E402
VAGAS.update(NOVAS)

from vagas_busca2 import NOVAS2  # noqa: E402
VAGAS.update(NOVAS2)

from vagas_busca3 import NOVAS3  # noqa: E402
VAGAS.update(NOVAS3)

from vagas_busca4 import NOVAS4  # noqa: E402
VAGAS.update(NOVAS4)

try:
    from vagas_busca5 import NOVAS5  # noqa: E402
    VAGAS.update(NOVAS5)
except ImportError:
    pass
