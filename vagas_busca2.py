"""Busca 05/10/2026 (LinkedIn público Brasil remoto + Curitiba, Programathor)."""
from vagas_busca1 import PERFORA, CLEARBOX, TRADING, TRADING_BACK, CEP, _resp

POWERBI = ("Estágio em Análise de Dados (Power BI) – Oregon Tool - 2026",
           "Construção e manutenção de dashboards e relatórios em Power BI para áreas de negócio de uma indústria multinacional, com tratamento e modelagem de dados, garantia de consistência das informações e apoio à tomada de decisão baseada em dados.")

NOVAS2 = {
    "11_4dfconnect_fullstack_js": dict(
        objetivo="Atuar como Desenvolvedor Full-Stack JavaScript Júnior na 4DF Connect, desenvolvendo e mantendo funcionalidades do front-end ao back-end com JavaScript e TypeScript, escrevendo código limpo e bem testado e participando de revisões de código e discussões técnicas com o time.",
        resumo="Estudante de Engenharia de Software (8º Período) com experiência full-stack em JavaScript e TypeScript demonstrada em projetos: um simulador de trading com frontend React e API REST própria em Node.js, e uma plataforma com app React Native integrada a backend Flask. Tenho forte cuidado com testes automatizados e qualidade (pytest, SonarCloud, CI/CD), uso Git no dia a dia e tenho facilidade para aprender novas tecnologias e trabalhar em equipe.",
        projetos=[TRADING, PERFORA],
        skill_cs=("JavaScript / TypeScript", "Intermediário"),
        respostas=_resp("4DF Connect – Full-Stack JavaScript Júnior (remoto, qualquer lugar do Brasil)", "https://www.linkedin.com/jobs/view/4475330847",
                        "- Pretensão: R$ 3.000 a R$ 4.000 CLT\n"),
    ),
    "12_wpp_media_programador_dados": dict(
        objetivo="Atuar como Programador Júnior de Dados na WPP Media em Curitiba, apoiando a implementação de soluções de mensuração, coleta de dados e tracking, automações em Google Cloud e projetos de analytics e BI, garantindo qualidade nas entregas e evoluindo junto ao time em diferentes clientes.",
        resumo="Estudante de Engenharia de Software (8º Período) que une programação e dados: estagiei em Análise de Dados com Power BI na Oregon Tool, desenvolvi uma biblioteca própria de controle estatístico em Python e integrações com APIs REST que processam dados estruturados (JSON). Tenho domínio de SQL, Python e Git, certificação em Data Science (Cisco), experiência com automações e facilidade para aprender ferramentas como GTM, GA4 e GCP rapidamente.",
        projetos=[POWERBI, CEP],
        skill_cs=("Python / Power BI", "Intermediário"),
        respostas=_resp("WPP Media – Programador(a) Júnior Dados e Programação (Curitiba ou SP)", "https://www.linkedin.com/jobs/view/4473190651",
                        "- Pretensão: R$ 3.000 a R$ 4.000 CLT\n\nObs.: a vaga cita GTM, GA4 e GCP. Se ainda não usou, vale fazer o curso gratuito de GA4 do Google (Skillshop) antes da entrevista. Modelo (presencial/híbrido) em Curitiba não informado.\n"),
    ),
    "13_notoria_fullstack_ia_saude": dict(
        objetivo="Atuar como Desenvolvedor Full Stack na NOTORIA, construindo SPAs em React e serviços integrados a bancos SQL e NoSQL, aplicando Inteligência Artificial em soluções para a área da saúde, com testes automatizados, Docker, pipelines de CI/CD e autonomia para propor e experimentar.",
        resumo="Estudante de Engenharia de Software (8º Período) com projetos completos que unem React e IA: desenvolvi sozinho uma plataforma SaaS de saúde nutricional que usa a Gemini API para analisar fotos de refeições, com backend Flask testado e CI/CD, e um simulador de trading em React e TypeScript. Tenho experiência prática com Docker e AWS, testes automatizados, bancos relacionais e cuidado com dados sensíveis (JWT, hash de senhas, LGPD).",
        projetos=[PERFORA, TRADING],
        skill_cs=("React / TypeScript", "Intermediário"),
        respostas=_resp("NOTORIA – Full Stack (100% remoto) – IA e Saúde", "https://www.linkedin.com/jobs/view/4472626093",
                        "- Pretensão: R$ 3.500 a R$ 4.500 CLT ou R$ 4.500 a R$ 6.000 PJ\n\nATENÇÃO: a vaga está marcada como 'Entry level', mas pede 'experiência sólida' com React, NoSQL e Jest/Cypress. Vale tentar: o Perfora (app de saúde com IA) conversa diretamente com o produto deles.\n"),
    ),
    "14_smartspace_dev_jr": dict(
        objetivo="Atuar como Pessoa Desenvolvedora de Software Júnior na Smartspace, construindo e evoluindo aplicações Full Stack das soluções SaaS, desenvolvendo APIs com Node.js e Java e interfaces responsivas em React, atuando lado a lado com QA, Produto e UX/UI do código à entrega.",
        resumo="Estudante de Engenharia de Software (8º Período) com base full-stack demonstrada em projetos: APIs REST em Node.js e Flask, frontend em React e TypeScript, e Java/Spring Boot no TCC, um estudo sobre testes em arquiteturas monolíticas e de microsserviços (JUnit 5, ArchUnit). Uso Git com CI/CD no dia a dia, tenho foco em qualidade e testes automatizados e gosto de trabalhar próximo de QA e Produto para entregar valor ao usuário.",
        projetos=[TRADING_BACK, PERFORA],
        skill_cs=("Node.js / React", "Intermediário"),
        respostas=_resp("Smartspace – Pessoa Desenvolvedora Software Júnior (remoto; sede em João Pessoa)", "https://www.linkedin.com/jobs/view/4472917380",
                        "- Pretensão: R$ 3.000 a R$ 4.000 CLT\n- Confirme se é 100% remoto (apareceu no filtro remoto do LinkedIn, mas a sede é em João Pessoa/PB).\n"),
    ),
    "15_egger_mesquita_dev_jr_curitiba": dict(
        objetivo="Atuar como Técnico de TI / Desenvolvedor Júnior na Egger e Mesquita em Curitiba, criando e mantendo robôs de automação de processos, desenvolvendo processos de ETL e integrações com bancos de dados, APIs e arquivos, com testes contínuos, monitoramento e atenção à segurança.",
        resumo="Estudante de Engenharia de Software (8º Período) com foco em automação e dados: mapeei processos e propus automações digitais em projeto com a Copel (MPS.BR), estagiei em Análise de Dados com Power BI e desenvolvo em Python integrações com APIs REST e bancos relacionais. Tenho experiência com testes automatizados, Git e boas práticas de segurança (prevenção de SQL injection, logs de auditoria), além de facilidade para aprender ferramentas de RPA.",
        projetos=[("Mapeamento de Processos e Avaliação de Maturidade Organizacional (MPS.BR) - Conclusão: 2025",
                   "Análise e modelagem dos processos de negócio de uma empresa do setor elétrico (Copel), utilizando o modelo MPS.BR. Condução de gap analysis, identificação de fragilidades operacionais e proposição de automações digitais para processos manuais e repetitivos."),
                  POWERBI],
        skill_cs=("Python / Automação", "Intermediário"),
        respostas=_resp("Egger e Mesquita Advogados – Técnico de TI (Desenvolvedor Jr.) – Curitiba", "https://www.linkedin.com/jobs/view/4472766369",
                        "- Pretensão: R$ 2.800 a R$ 3.500 CLT (escritório de advocacia, vaga de técnico)\n\nObs.: o foco é RPA (Automation Anywhere) e ETL, mais próximo de automação do que de desenvolvimento de produto. Provavelmente presencial em Curitiba.\n"),
    ),
}
