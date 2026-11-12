"""Busca 05/11/2026 – Vagas Júnior não-estágio selecionadas a partir do radar automático.
Fontes: Remotar, GitHub (soujava, backend-br), Gupy.
Importado no final de vagas.py.
"""
from vagas_busca1 import PERFORA, CLEARBOX, TRADING, TRADING_BACK, _resp
from vagas_busca3 import TCC

SEGURANCA_SW = (
    "Segurança de Software & Autenticação Segura (Python / MVC) - Conclusão: 2026",
    "Desenvolvimento de aplicação segura com arquitetura MVC em Python: hash criptográfico com bcrypt, prevenção de SQL injection por queries parametrizadas, bloqueio de contas por tentativas e logs de auditoria para rastreabilidade de eventos de segurança."
)

OREGON_TOOL = (
    "Estágio em Análise de Dados e Automação – Oregon Tool - 2026",
    "Análise de dados e automação de relatórios com Python, SQL, Excel e Power BI em indústria multinacional, garantindo integridade de métricas e apoiando decisões operacionais baseadas em dados."
)

NOVAS4 = {
    "19_it4us_pentester_jr_ia": dict(
        objetivo="Atuar como Pentester Júnior na It4us, identificando vulnerabilidades em sistemas web, APIs e redes, conduzindo testes de intrusão e aplicando ferramentas de Inteligência Artificial para automação de testes ofensivos e segurança de aplicações.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR) com certificações Cisco em Cibersegurança Júnior (2026), Segurança de Endpoint (2024) e Python. Desenvolvi projetos com foco em segurança (autenticação JWT, hash de senhas com bcrypt, prevenção de SQL injection e logs de auditoria) e integro IA generativa ao fluxo de desenvolvimento e testes. Inglês avançado para leitura de CVEs e redação de relatórios técnicos.",
        projetos=[SEGURANCA_SW, PERFORA],
        skill_cs=("Cibersegurança / IA", "Intermediário"),
        respostas=_resp(
            "It4us – Pentester Júnior (com foco em IA) (100% Remoto)",
            "https://it4us-trial.inhire.app/vagas/6ecb6110-0973-4591-b950-88e5ffb58ac1/pentester-junior",
            "- Modalidade: 100% Remoto\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.500 CLT (ou R$ 4.500 a R$ 6.000 PJ), negociável\n"
            "- Certificações Cisco para citar: Analista de Cibersegurança Júnior (2026), Segurança de Endpoint (2024), Python (2023)\n"
            "- Destaques: mencione o Perfora (autenticação JWT, rate limiting contra brute-force, SonarCloud) e o projeto acadêmico de segurança MVC (bcrypt, prevenção a SQL injection).\n"
        ),
    ),
    "20_sylision_dev_java_jr_pix": dict(
        objetivo="Atuar como Desenvolvedor(a) Java Júnior no time de pagamentos Pix, desenvolvendo endpoints REST resilientes, implementando regras transacionais com Spring Boot e PostgreSQL, garantindo alta cobertura de testes automatizados e integrando microsserviços conteinerizados.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR) com sólida base em Java e qualidade de código: no TCC realizo estudo empírico sobre arquitetura e testes em Java/Spring Boot utilizando JUnit 5, ArchUnit e mutation testing (Pitest). Desenvolvi aplicações com regras transacionais, persistência em bancos relacionais com SQL, conteinerização com Docker e pipelines de CI/CD.",
        projetos=[TCC, TRADING_BACK],
        skill_cs=("Java / Spring Boot", "Intermediário"),
        respostas=_resp(
            "Sylision – Desenvolvedor(a) Java Júnior (Pagamentos via Pix) (100% Remoto)",
            "https://github.com/soujava/vagas-java/issues/1975",
            "- Modalidade: 100% Remoto (CLT ou PJ)\n"
            "- Candidatura: enviar currículo para tech@sylision.com ou aplicar via link indicado na issue\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.500 CLT ou R$ 4.500 a R$ 6.000 PJ\n"
            "- Destaque técnico: enfatize o TCC em Java/Spring Boot com JUnit 5 e testes de mutação (Pitest), e a experiência com regras transacionais no Simulador de Trading.\n"
        ),
    ),
    "21_byx_dev_backend_python_jr": dict(
        objetivo="Atuar como Desenvolvedor Backend Python Júnior na byx, construindo e mantendo APIs RESTful escaláveis, integrando microsserviços, estruturando dados em bancos relacionais e garantindo confiabilidade por meio de testes automatizados e integração contínua.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR) com Python como principal linguagem desde 2023 (certificação Cisco Networking Academy): implementei backend REST em camadas com Flask, autenticação JWT, rate limiting e suíte pytest com quality gate no SonarCloud. Domino modelagem relacional com SQL (MySQL/SQLite), Docker, Git e desenvolvimento orientado a testes.",
        projetos=[PERFORA, CLEARBOX],
        skill_cs=("Python / Flask", "Intermediário"),
        respostas=_resp(
            "byx – Desenvolvedor Backend Python JR (100% Remoto)",
            "https://byx.inhire.app/vagas/aa87848b-9004-46a7-b54e-b00c74a07a03/desenvolvedor-backend-python-jr",
            "- Modalidade: 100% Remoto\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.500 CLT (negociável)\n"
            "- Destaques: GitHub (github.com/claudioc0) com destaque para o Perfora (backend Flask em camadas com pytest e CI/CD SonarCloud) e ClearBox (LLMs e APIs REST).\n"
        ),
    ),
    "22_grupo_olx_frontend_jr": dict(
        objetivo="Atuar como Pessoa Desenvolvedora Front-end Júnior no Grupo OLX (Seller Management), transformando requisitos de produto em interfaces React e TypeScript rápidas, acessíveis e reutilizáveis, consumindo APIs RESTful e garantindo experiência fluida para os usuários.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR) com experiência front-end em React e TypeScript demonstrada em projetos: construí o Simulador de Trading com telas de ordens, cotações e carteira com tratamento de estados (loading, erro e vazio) e app em React Native. Tenho atenção a design responsivo, componentização limpa, consumo de APIs e uso IA agêntica validando criticamente o código gerado.",
        projetos=[TRADING, PERFORA],
        skill_cs=("React / TypeScript", "Intermediário"),
        respostas=_resp(
            "Grupo OLX – Pessoa Desenvolvedora Front-end Jr (Seller Management) (100% Remoto)",
            "https://vemsergrupoolx.gupy.io/job/eyJqb2JJZCI6MTI3NTcyNDIsInNvdXJjZSI6InJlbW90YXIifQ==?jobBoardSource=remotar",
            "- Modalidade: 100% Remoto (Gupy)\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.500 CLT\n"
            "- Dica Gupy: Faça upload do PDF gerado nesta pasta e revise se o perfil Gupy puxou corretamente os projetos em React/TypeScript e o estágio na Oregon Tool.\n"
        ),
    ),
    "23_db1_dev_java_jr": dict(
        objetivo="Atuar como Dev Java Júnior na DB1 Global Software, desenvolvendo microsserviços e integrações para o ANYMARKET com Java e Spring Boot, otimizando consultas em bancos relacionais e escrevendo testes automatizados de alta cobertura em ambiente ágil.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR, residente no Paraná) com forte dedicação a Java: no TCC analiso comparativamente arquiteturas monolíticas e microsserviços em Java/Spring Boot com JUnit 5, ArchUnit e testes de mutação (Pitest). Experiência prática com Git, Docker, modelagem de dados SQL e facilidade para evoluir sistemas complexos junto ao time.",
        projetos=[TCC, PERFORA],
        skill_cs=("Java / Spring Boot", "Intermediário"),
        respostas=_resp(
            "DB1 Global Software / ANYMARKET – Dev Java Junior (Remoto / Paraná)",
            "https://github.com/backend-br/vagas/issues/12444",
            "- Modalidade: 100% Remoto (empresa com sede em Maringá/PR, você reside na Grande Curitiba/PR)\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.200 CLT\n"
            "- Inscrição: formulário DB1 ou link indicado na issue do GitHub\n"
            "- Destaque local: ressalte que estuda na PUCPR (PR) e que seu TCC é focado em testes em Java/Spring Boot com arquitetura de microsserviços.\n"
        ),
    ),
    "24_vonbz_dev_typescript_jr": dict(
        objetivo="Atuar como Desenvolvedor(a) de Software Júnior na VONBZ, desenvolvendo soluções escaláveis para a plataforma digital de mobilidade elétrica com TypeScript, integrando APIs RESTful, modelando dados e colaborando com o time na evolução ágil da arquitetura.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR) com forte raciocínio lógico e domínio de TypeScript demonstrado em projetos: desenvolvi frontend (React) e backend (Node.js) com consumo e exposição de APIs REST, validação de regras de negócio e tratamento de estados assíncronos. Tenho forte base em orientação a objetos, testes automatizados, Git e facilidade para aprender novas linguagens como Elixir.",
        projetos=[TRADING_BACK, TRADING],
        skill_cs=("TypeScript / Node.js", "Intermediário"),
        respostas=_resp(
            "VONBZ – Desenvolvedor(a) de Software TypeScript / Elixir Júnior (100% Remoto)",
            "https://vonbz.inhire.app/vagas/31c10560-fdcc-492a-a8a0-0730254c331a/desenvolvedora-de-software-typescript-elixir-or-junior-or-remoto-or-mobilidade-eletrica",
            "- Modalidade: 100% Remoto (Mobilidade Elétrica e Tecnologia)\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.500 CLT (ou R$ 4.500 a R$ 5.500 PJ)\n"
            "- Destaque técnico: enfatize a vivência com TypeScript no backend e frontend, domínio de APIs e a participação no projeto com a Copel (mobilidade / setor elétrico).\n"
        ),
    ),
    "25_bip_brasil_dev_ia_rpa_jr": dict(
        objetivo="Atuar como Pessoa Desenvolvedora de IA e RPA Júnior na BIP Brasil, desenvolvendo agentes inteligentes e automações de processos de negócio, integrando modelos de linguagem a sistemas corporativos e otimizando fluxos com foco em qualidade e escalabilidade.",
        resumo="Estudante de Engenharia de Software (8º Período, PUCPR) que une IA generativa e automação de processos: desenvolvi plataforma SaaS com Gemini API (Perfora) e classificador com LLMs (ClearBox), mapeei processos operacionais e propus automações no projeto com a Copel (MPS.BR) e estagiei em análise de dados na multinacional Oregon Tool. Domínio de Python, APIs REST, SQL e testes automatizados.",
        projetos=[PERFORA, ("Mapeamento de Processos e Automações Digitais (PUCPR / Copel) - Conclusão: 2025",
                            "Análise e modelagem de processos de negócio de distribuidora de energia (Copel) via MPS.BR. Condução de gap analysis e proposição de automações digitais para eliminação de tarefas manuais e repetitivas.")],
        skill_cs=("IA Generativa / RPA", "Intermediário"),
        respostas=_resp(
            "BIP Brasil – Pessoa Desenvolvedora de IA/RPA - Junior (100% Remoto, Gupy)",
            "https://vemprabip.gupy.io/job/eyJqb2JJZCI6MTI4NDQ3ODAsInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0=?jobBoardSource=gupy_portal",
            "- Modalidade: 100% Remoto (Gupy)\n"
            "- Pretensão salarial: R$ 3.500 a R$ 4.500 CLT (consultoria multinacional, pacote completo de benefícios)\n"
            "- Destaques no perfil Gupy: fixe Perfora (IA / LLMs), projeto Copel (MPS.BR / automação) e estágio na Oregon Tool.\n"
        ),
    ),
}
