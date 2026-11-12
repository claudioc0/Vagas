"""Busca 05/10/2026 – Gupy (remoto + Paraná). Repositórios GitHub/Remotive/Himalayas sem vagas aderentes."""
from vagas_busca1 import PERFORA, TRADING, TRADING_BACK, _resp

TCC = ("TCC: Testes em Arquitetura Monolítica vs. Microsserviços (Java/Spring Boot) - Conclusão: 2026",
       "Estudo comparativo em Java/Spring Boot sobre cobertura de testes, conformidade arquitetural e mutation score entre as duas arquiteturas, utilizando JUnit 5, ArchUnit, Pitest e JaCoCo, com aplicação de padrões de projeto e boas práticas de orientação a objetos.")

NOVAS3 = {
    "16_zenvia_dev_operacoes_jr": dict(
        objetivo="Atuar como Desenvolvedor(a) de Operações Júnior na Zenvia, garantindo entregas de valor por meio das plataformas de comunicação e IA da empresa, implementando soluções com JavaScript e JSON, documentando o que for construído e participando das cerimônias ágeis das squads.",
        resumo="Estudante de Engenharia de Software (8º Período) com base sólida em lógica de programação, JavaScript/TypeScript e integração de sistemas via APIs REST e JSON. Desenvolvi aplicações completas que usam IA, como um classificador de e-mails que sugere respostas automaticamente e um SaaS integrado à Gemini API. Tenho boa comunicação escrita, organização para documentar soluções, inglês avançado e facilidade para aprender novas tecnologias.",
        projetos=[("ClearBox – Classificador Inteligente de E-mails com IA - Conclusão: 2026",
                   "Aplicação que utiliza modelos de linguagem para classificar mensagens como produtivas ou improdutivas, sugerir automaticamente uma resposta adequada e exibir o percentual de confiabilidade, automatizando a triagem e o atendimento de mensagens."),
                  PERFORA],
        skill_cs=("JavaScript / JSON", "Intermediário"),
        respostas=_resp("Zenvia – Desenvolvedor(a) Operações Junior (remoto)",
                        "https://zenvia.gupy.io/job/eyJqb2JJZCI6MTI0OTM5OTcsInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0=?jobBoardSource=gupy_portal",
                        "- Pretensão: R$ 3.000 a R$ 4.000 CLT\n- Não exige experiência: pede lógica, noções de JS/JSON e comunicação.\nObs.: na Gupy, use o currículo PDF desta pasta e revise o perfil Gupy (ele pré-preenche os campos).\n"),
    ),
    "17_ciee_pr_dev_sistemas_curitiba": dict(
        objetivo="Atuar como Desenvolvedor de Sistemas no CIEE-PR em Curitiba, desenvolvendo e mantendo aplicações web com C#/.NET e Angular ou React, criando APIs RESTful, evoluindo bancos SQL Server e contribuindo com a pesquisa e aplicação de Inteligência Artificial em soluções inovadoras.",
        resumo="Estudante de Engenharia de Software (8º Período) com base sólida em C#/.NET e orientação a objetos, frontend em React e TypeScript e bancos de dados relacionais com SQL. Desenvolvi APIs RESTful com autenticação e testes automatizados (TDD, pytest, JUnit) e uma plataforma integrada à IA Generativa. Tenho familiaridade com Git no dia a dia, boas práticas de segurança e facilidade para aprender e evoluir sistemas já existentes junto ao time.",
        projetos=[PERFORA, TRADING],
        respostas=_resp("CIEE-PR – Desenvolvedor de Sistemas (presencial, Curitiba)",
                        "https://ciee-pr.gupy.io/job/eyJqb2JJZCI6MTIzNzkwNDAsInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0=?jobBoardSource=gupy_portal",
                        "- Pretensão: R$ 3.500 a R$ 4.500 CLT\n\nATENÇÃO: pede 'Superior em Computação/Eng. de Software' (talvez exija o curso completo; você forma em 12/2026) e 'experiência em C#/.NET e SQL Server'. A 6ª barra do currículo ficou como C#/.NET, igual ao original. Benefícios bons: Unimed, bolsa de pós e jornada de 7h30.\n"),
    ),
    "18_geopixel_analista_dev_jr": dict(
        objetivo="Atuar como Analista Desenvolvedor Júnior na Geopixel, desenvolvendo módulos e funcionalidades com Java e JavaScript, aplicando orientação a objetos, padrões de projeto e testes automatizados unitários, de integração e aceitação, e evoluindo com o time em soluções para clientes.",
        resumo="Estudante de Engenharia de Software (8º Período) com Java, JavaScript, HTML e CSS demonstrados em projetos e repositório público. No TCC uso Java/Spring Boot para comparar arquiteturas com JUnit 5, ArchUnit e mutation testing, e desenvolvi um simulador de trading em React e TypeScript. Tenho domínio de orientação a objetos e estruturas de dados, bancos relacionais com SQL, Git no dia a dia e inglês avançado para leitura técnica.",
        projetos=[TCC, TRADING],
        skill_cs=("Java / Spring Boot", "Intermediário"),
        respostas=_resp("Geopixel – Analista Desenvolvedor Júnior (remoto)",
                        "https://geopixel.gupy.io/job/eyJqb2JJZCI6MTI2MDUzNjQsInNvdXJjZSI6Imd1cHlfcG9ydGFsIn0=?jobBoardSource=gupy_portal",
                        "- Pretensão: R$ 3.000 a R$ 4.000 CLT\n- Aceita 'repositório de códigos OU experiência profissional'. Deixe o repo do TCC (Java/Spring) e o do simulador públicos.\n\nATENÇÃO: pede disponibilidade para viagens a clientes (CNH é diferencial) e PostgreSQL (você tem SQL/MySQL).\n"),
    ),
}
