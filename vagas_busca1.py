"""Busca 03/10/2026 (stackvagas.dev). Importado no final de vagas.py."""

PERFORA = ("Desenvolvimento de Plataforma SaaS (Perfora) Integrada à Inteligência Artificial - Conclusão: 2026",
           "Implementação full-stack de uma aplicação client-server: backend Flask em camadas com APIs RESTful, autenticação JWT, hash de senha e rate limiting, app em React Native e integração com IA Generativa (Gemini API) para analisar imagens e retornar dados estruturados (JSON). Suíte de testes pytest e pipeline CI/CD (Azure DevOps + SonarCloud).")
CLEARBOX = ("ClearBox – Classificador Inteligente de E-mails com IA - Conclusão: 2026",
            "Aplicação que utiliza modelos de linguagem para classificar e-mails como produtivos ou improdutivos, sugerir automaticamente uma resposta adequada e exibir o percentual de confiabilidade da classificação, automatizando a triagem de mensagens.")
TRADING = ("Simulador de Trading Educacional (React + TypeScript) - Conclusão: 2026",
           "Site educacional de trading simulado (ações, cripto e memecoins) para iniciantes, sem dinheiro real. Frontend em React e TypeScript com telas de cotações, carteira e ordens, consumindo uma API REST própria em Node.js/SQLite e tratando estados de carregamento, erro e dados vazios.")
TRADING_BACK = ("Simulador de Trading Educacional (Node.js + TypeScript) - Conclusão: 2026",
                "Plataforma de trading simulado (ações, cripto e memecoins) para iniciantes: API REST própria em Node.js com persistência em SQLite para usuários, carteiras e ordens, consumida por um frontend em React e TypeScript, com tratamento de erros e validação das operações.")
XADREZ = ("Jogo de Xadrez com Modo Carreira (Godot Engine) - Conclusão: 2025",
          "Jogo desktop de xadrez em pixel art com regras ortodoxas e modo carreira narrativo próprio, desenvolvido em GDScript: lógica de estado do tabuleiro, validação de jogadas, input do jogador, animações e feedback visual, com foco na experiência do jogador.")
CEP = ("Biblioteca de Controle Estatístico de Processos em Python - Conclusão: 2025",
       "Implementação própria, em Python/Jupyter, de gráficos de controle estatístico (XbarR, XbarS, XmR e XMmR) para análise de dados de processos, incluindo cálculo de limites de controle e identificação de pontos fora de controle, com código orientado a objetos.")


def _resp(titulo, link, extra):
    return (f"# {titulo}\nLink: {link}\n\n- Currículo: Curriculo_Claudio_Colombo.pdf (nesta pasta)\n"
            f"- GitHub: https://github.com/claudioc0\n- LinkedIn: https://www.linkedin.com/in/claudio-colombo-ferreira\n{extra}")


NOVAS = {
    "05_bluelephant_python_ia": dict(
        objetivo="Atuar como Desenvolvedor Python e IA na Bluelephant, desenvolvendo serviços backend e APIs que conectam agentes de IA a sistemas reais, integrando modelos de linguagem com RAG, chamadas de ferramentas e extração estruturada de dados, com testes automatizados e atenção à LGPD.",
        resumo="Estudante de Engenharia de Software (8º Período) com Python como linguagem principal e experiência prática integrando LLMs a backends: construí uma API Flask em camadas (JWT, rate limiting, pytest, CI/CD) que usa a Gemini API para extrair dados estruturados de imagens, e um classificador de e-mails com IA. Tenho domínio de orientação a objetos, bancos relacionais, Git, noções de Docker e AWS, leitura técnica em inglês e cuidado com dados sensíveis.",
        projetos=[PERFORA, CLEARBOX],
        skill_cs=("Python / Flask", "Intermediário"),
        respostas=_resp("Bluelephant – Desenvolvedor Python e IA (Curitiba)", "https://www.linkedin.com/jobs/view/4470869666",
                        "- Pretensão: R$ 3.500 a R$ 4.500 CLT\n\nATENÇÃO: pedem 1-2 anos de Python e 'pelo menos uma API que rodou em produção (vamos pedir para você mostrar)'. Deixe o Perfora rodando (deploy ou demo). Modelo de trabalho não informado; a consultoria fica em Curitiba.\n"),
    ),
    "06_jungle_gaming_backend": dict(
        objetivo="Atuar como Desenvolvedor Back-end Júnior na Jungle Gaming, implementando endpoints REST e fluxos em tempo real com TypeScript, evoluindo modelos e consultas em bancos relacionais, contribuindo com microsserviços e Docker e aprendendo NestJS, DDD e AWS com acompanhamento próximo do time.",
        resumo="Estudante de Engenharia de Software (8º Período) com base em backend demonstrada em projetos: APIs REST em Node.js e Flask com autenticação JWT, rate limiting, SQL e testes automatizados. No TCC estudo testes em arquiteturas monolíticas e de microsserviços (JUnit, ArchUnit, mutation testing). Tenho experiência prática com Docker e AWS, uso Git e ferramentas de IA agêntica no dia a dia, validando criticamente o código gerado, e gosto muito de jogos.",
        projetos=[TRADING_BACK, PERFORA],
        skill_cs=("Node.js / TypeScript", "Intermediário"),
        respostas=_resp("Jungle Gaming – Desenvolvedor Back-end Junior (remoto, R$ 2.500–5.000)", "https://www.linkedin.com/jobs/view/4472161575",
                        "- Pretensão: R$ 4.000\n- Mensagem: 'Construí APIs REST em Node.js e Flask (JWT, rate limiting, testes, CI/CD) e estudo microsserviços no TCC. Gosto de games (desenvolvi um xadrez em Godot) e quero crescer em NestJS/DDD com o time.'\n"),
    ),
    "07_jungle_gaming_frontend_jogos": dict(
        objetivo="Atuar como Desenvolvedor Front-end Júnior de Jogos na Jungle Gaming, transformando conceitos de game design e arte em experiências jogáveis e responsivas com React, TypeScript e PixiJS, integrando o estado do jogo a APIs REST e WebSockets e testando fluidez em dispositivos reais.",
        resumo="Estudante de Engenharia de Software (8º Período) apaixonado por jogos e interfaces: desenvolvi um jogo de xadrez em Godot com modo carreira, lidando com estado do jogo, input, animações e feedback visual, e um simulador de trading em React e TypeScript consumindo API própria. Tenho atenção à performance, à responsividade e à depuração de problemas de estado, e uso ferramentas de IA agêntica no dia a dia, validando criticamente o código gerado.",
        projetos=[XADREZ, TRADING],
        skill_cs=("React / TypeScript", "Intermediário"),
        respostas=_resp("Jungle Gaming – Front-end Junior – Jogos (remoto)", "https://www.linkedin.com/jobs/view/4472151935",
                        "- Pretensão: R$ 4.000\n- Mensagem: 'Desenvolvi um xadrez com modo carreira em Godot (estado do tabuleiro, input, animações) e um simulador de trading em React+TS. Juntar games e frontend é exatamente o que procuro; estou estudando PixiJS.'\nDica: fixe o repositório do xadrez no GitHub, com GIF no README.\n"),
    ),
    "08_tqi_fullstack_node": dict(
        objetivo="Atuar como Engenheiro de Software Fullstack Júnior na TQI, desenvolvendo aplicações com Node.js e React em times ágeis, criando provas de conceito com tecnologias emergentes, implementando testes automatizados e trazendo o uso de IA no desenvolvimento para gerar inovação.",
        resumo="Estudante de Engenharia de Software (8º Período) com experiência full-stack em projetos: React e TypeScript no frontend, APIs REST em Node.js e Flask no backend e bancos relacionais (MySQL, SQLite). Tenho forte base em testes e qualidade (pytest, JUnit, mutation testing, SonarCloud), noções práticas de Docker, AWS e CI/CD, e uso IA no desenvolvimento de forma crítica (Claude Code, Cursor). Inglês avançado para documentação técnica.",
        projetos=[TRADING, PERFORA],
        skill_cs=("Node.js / React", "Intermediário"),
        respostas=_resp("TQI – Fullstack Node.js Júnior (100% remoto, CLT)", "https://www.linkedin.com/jobs/view/4470166394",
                        "- Pretensão: R$ 3.500 a R$ 4.000 CLT (VA/VR R$ 1.060 + PLR)\n- Inglês técnico: avançado\n"),
    ),
    "09_solfy_dev_jr": dict(
        objetivo="Atuar como Desenvolvedor Júnior na Solfy, desenvolvendo e mantendo aplicações web escaláveis com React, Next.js e TypeScript, integrando APIs REST e bancos relacionais, corrigindo bugs, otimizando desempenho e colaborando com produto e design na criação de interfaces modernas.",
        resumo="Estudante de Engenharia de Software (8º Período) com React e TypeScript demonstrados em projetos: um simulador de trading com cotações, carteira e ordens consumindo API REST própria, e um app React Native integrado a um backend Flask. Tenho experiência com bancos relacionais, Git, testes automatizados, Docker e CI/CD com SonarCloud, além de noções de UI/UX e design responsivo. Aprendo rápido e gosto de evoluir sistemas com o time.",
        projetos=[TRADING, PERFORA],
        skill_cs=("React / TypeScript", "Intermediário"),
        respostas=_resp("Solfy – Desenvolvedor de Software Jr. (remoto, horário flexível)", "https://www.linkedin.com/jobs/view/4473767031",
                        "- Pretensão: R$ 3.000 a R$ 4.000\n\nATENÇÃO: pedem Next.js (SSR/SSG), que não está no seu contexto. Se já usou, cite; se não, vale um mini projeto antes da entrevista.\n"),
    ),
    "10_bairesdev_python_jr": dict(
        objetivo="Atuar como Desenvolvedor Python Júnior na BairesDev, construindo e mantendo aplicações e componentes Python com código limpo, participando de revisões de código, apoiando testes e debug e aprendendo frameworks e boas práticas com engenheiros experientes em projetos globais.",
        resumo="Estudante de Engenharia de Software (8º Período) com Python como linguagem principal desde 2023 (certificação Cisco): construí um backend Flask em camadas com JWT, rate limiting e suíte pytest, uma biblioteca estatística própria e aplicações com IA. Tenho domínio de orientação a objetos, bancos de dados relacionais, Git e fluxos colaborativos com CI/CD. Inglês avançado e facilidade para aprender novas tecnologias rapidamente.",
        projetos=[PERFORA, CEP],
        skill_cs=("Python / Flask", "Intermediário"),
        respostas=_resp("BairesDev – Desenvolvedor Python Júnior (100% remoto)", "https://www.linkedin.com/jobs/view/4472324313",
                        "- Pretensão: em USD ~1.200–1.800/mês (contractor); em BRL R$ 5.000–6.000 PJ\n- Processo longo, com testes técnicos em inglês.\nObs.: a BairesDev republica a mesma vaga várias vezes; uma candidatura basta. Alinha com sua meta de remoto pago em moeda forte.\n"),
    ),
}
