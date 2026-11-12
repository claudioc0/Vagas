"""adicionar_vaga.py – Gerador semi-automático de candidaturas completas:
1. Identifica a vaga (por número do radar, por URL ou manualmente).
2. Classifica a stack e escolhe os 2 melhores projetos do portfólio de Claudio Colombo.
3. Redige o Objetivo, Resumo e Respostas customizadas.
4. Registra no ecossistema (vagas_busca5.py e vagas.py).
5. Executa a geração do PowerPoint e exportação do PDF via PowerPoint COM.

Uso:
  python adicionar_vaga.py --list                 (lista o Top 20 novas vagas do radar)
  python adicionar_vaga.py 1                      (gera a pasta da vaga #1 do radar)
  python adicionar_vaga.py <url>                  (gera a pasta a partir da URL)
  python adicionar_vaga.py --manual               (modo interativo manual)
"""

import argparse
import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

BASE_DIR = Path(__file__).parent
BUSCA_JSON = BASE_DIR / "busca" / "vagas_encontradas.json"

# =====================================================================
# CATÁLOGO DE PROJETOS DE CLAUDIO COLOMBO
# =====================================================================
PERFORA = (
    "Desenvolvimento de Plataforma SaaS (Perfora) Integrada à Inteligência Artificial - Conclusão: 2026",
    "Implementação full-stack de uma aplicação client-server: backend Flask em camadas com APIs RESTful, autenticação JWT, hash de senha e rate limiting, app em React Native e integração com IA Generativa (Gemini API) para analisar imagens e retornar dados estruturados (JSON). Suíte de testes pytest e pipeline CI/CD (Azure DevOps + SonarCloud)."
)
CLEARBOX = (
    "ClearBox – Classificador Inteligente de E-mails com IA - Conclusão: 2026",
    "Aplicação que utiliza modelos de linguagem para classificar e-mails como produtivos ou improdutivos, sugerir automaticamente uma resposta adequada e exibir o percentual de confiabilidade da classificação, automatizando a triagem de mensagens."
)
TRADING = (
    "Simulador de Trading Educacional (React + TypeScript) - Conclusão: 2026",
    "Site educacional de trading simulado (ações, cripto e memecoins) para iniciantes, sem dinheiro real. Frontend em React e TypeScript com telas de cotações, carteira e ordens, consumindo uma API REST própria em Node.js/SQLite e tratando estados de carregamento, erro e dados vazios."
)
TRADING_BACK = (
    "Simulador de Trading Educacional (Node.js + TypeScript) - Conclusão: 2026",
    "Plataforma de trading simulado (ações, cripto e memecoins) para iniciantes: API REST própria em Node.js com persistência em SQLite para usuários, carteiras e ordens, consumida por um frontend em React e TypeScript, com tratamento de erros e validação das operações."
)
TCC = (
    "Pesquisa (TCC): Estudo Empírico de Qualidade de Testes em Microsserviços e Monólitos (Java / Spring Boot)",
    "Investigação experimental comparando monolito e microsserviços em Java: implementação com Spring Boot, suíte de testes com JUnit 5, conformidade arquitetural com ArchUnit e mutação com Pitest para medir resiliência da cobertura."
)
SEGURANCA_SW = (
    "Segurança de Software & Autenticação Segura (Python / MVC) - Conclusão: 2026",
    "Desenvolvimento de aplicação segura com arquitetura MVC em Python: hash criptográfico com bcrypt, prevenção de SQL injection por queries parametrizadas, bloqueio de contas por tentativas e logs de auditoria para rastreabilidade de eventos de segurança."
)
OREGON_TOOL = (
    "Estágio em Análise de Dados e Automação – Oregon Tool - 2026",
    "Análise de dados e automação de relatórios com Python, SQL, Excel e Power BI em indústria multinacional, garantindo integridade de métricas e apoiando decisões operacionais baseadas em dados."
)
COPEL = (
    "Mapeamento de Processos e Automações Digitais (PUCPR / Copel) - Conclusão: 2025",
    "Análise e modelagem de processos de negócio de distribuidora de energia (Copel) via MPS.BR. Condução de gap analysis e proposição de automações digitais para eliminação de tarefas manuais e repetitivas."
)


def get_next_slug(company, title):
    """Calcula o próximo número de pasta e gera um slug limpo sem acentos."""
    existing_dirs = [d.name for d in BASE_DIR.iterdir() if d.is_dir() and re.match(r"^\d+_", d.name)]
    max_num = 0
    for d in existing_dirs:
        m = re.match(r"^(\d+)_", d)
        if m:
            max_num = max(max_num, int(m.group(1)))
    next_num = max_num + 1

    clean_company = strip_accents(company.lower().strip())
    clean_company = re.sub(r"[^a-z0-9]", "_", clean_company)
    clean_company = re.sub(r"_+", "_", clean_company).strip("_")

    clean_title = strip_accents(title.lower().strip())
    clean_title = re.sub(r"[^a-z0-9]", "_", clean_title)
    clean_title = re.sub(r"_+", "_", clean_title).strip("_")

    for prefix in ["desenvolvedor_a_", "desenvolvedor_", "pessoa_desenvolvedora_", "analista_de_", "vaga_"]:
        if clean_title.startswith(prefix):
            clean_title = clean_title[len(prefix):]

    comp_short = clean_company[:12].rstrip("_")
    title_short = clean_title[:25].rstrip("_")

    return f"{next_num:02d}_{comp_short}_{title_short}"


def classify_vacancy(title, company, description):
    """Classifica a vaga em um domínio técnico e define a melhor estratégia de CV."""
    text = f"{title} {company} {description}".lower()

    # 1. Java / Spring Boot
    if any(k in text for k in ["java", "spring", "spring boot", "springboot", "soujava"]):
        return {
            "domain": "JAVA",
            "skill_cs": ("Java / Spring Boot", "Intermediário"),
            "projetos": [TCC, TRADING_BACK],
            "role_focus": "Java e Spring Boot",
            "pitch_focus": "o TCC empírico focado em testes em microsserviços Java/Spring Boot (JUnit 5, ArchUnit e testes de mutação) e as regras transacionais no Simulador de Trading"
        }

    # 2. Cibersegurança / Pentest
    if any(k in text for k in ["pentest", "cibersegurança", "cybersecurity", "segurança da informação", "appsec"]):
        return {
            "domain": "CYBERSEC",
            "skill_cs": ("Cibersegurança / IA", "Intermediário"),
            "projetos": [SEGURANCA_SW, PERFORA],
            "role_focus": "Segurança de Aplicações e Pentest",
            "pitch_focus": "as certificações Cisco (Analista de Cibersegurança Jr, Segurança de Endpoint), a implementação de autenticação segura (JWT, bcrypt, prevenção a SQL injection) e o uso de IA para testes defensivos e ofensivos"
        }

    # 3. Dados / RPA / Automação
    if any(k in text for k in ["power bi", "analytics", "rpa", "automação", "processos", "ciência de dados", "dados"]):
        return {
            "domain": "DADOS_RPA",
            "skill_cs": ("Dados / Automação", "Intermediário"),
            "projetos": [OREGON_TOOL, COPEL],
            "role_focus": "Dados e Automação de Processos",
            "pitch_focus": "o estágio na multinacional Oregon Tool com análise de dados e automação (Python, SQL, Power BI) e o projeto de mapeamento e automação de processos na Copel (MPS.BR)"
        }

    # 4. Frontend / Full Stack (React / TypeScript)
    if any(k in text for k in ["react", "frontend", "front-end", "typescript", "angular", "vue", "next.js", "nextjs", "javascript"]):
        return {
            "domain": "FULLSTACK_JS",
            "skill_cs": ("React / TypeScript", "Intermediário"),
            "projetos": [TRADING, PERFORA],
            "role_focus": "Full Stack com React e TypeScript",
            "pitch_focus": "o Simulador de Trading com interfaces em React/TypeScript, gerenciamento de estados assíncronos e consumo de APIs REST, além do app React Native e backend no Perfora"
        }

    # 5. Python / IA Generativa
    if any(k in text for k in ["python", "ia", "inteligência artificial", "llm", "genai", "prompt", "fastapi", "flask"]):
        return {
            "domain": "PYTHON_IA",
            "skill_cs": ("Python / IA Generativa", "Intermediário"),
            "projetos": [PERFORA, CLEARBOX],
            "role_focus": "Python e Inteligência Artificial",
            "pitch_focus": "o Perfora (backend REST em Flask integrado à Gemini API para visão computacional, com pytest e CI/CD SonarCloud) e o ClearBox (classificação inteligente de e-mails com LLMs)"
        }

    # 6. Backend Geral
    return {
        "domain": "BACKEND_GERAL",
        "skill_cs": ("Backend / APIs REST", "Intermediário"),
        "projetos": [PERFORA, TRADING_BACK],
        "role_focus": "Desenvolvimento Backend",
        "pitch_focus": "o desenvolvimento de APIs RESTful em camadas, autenticação segura (JWT/bcrypt), modelagem relacional SQL e suíte de testes automatizados com CI/CD"
    }


def build_candidate_package(vaga_info):
    """Gera objetivo, resumo e respostas formatadas sob medida para a vaga."""
    title = vaga_info.get("title", "").strip()
    company = vaga_info.get("company", "").strip()
    location = vaga_info.get("location", "").strip()
    modality = vaga_info.get("modality", "Remoto").strip()
    url = vaga_info.get("url", "").strip()
    source = vaga_info.get("source", "").strip()
    desc = vaga_info.get("description", "").strip()

    strategy = classify_vacancy(title, company, desc)

    # 1. Objetivo sob medida
    if strategy["domain"] == "JAVA":
        objetivo = (f"Atuar como Desenvolvedor(a) Java Júnior na {company}, implementando endpoints REST resilientes com Spring Boot, "
                    f"estruturando regras transacionais em bancos relacionais, escrevendo testes automatizados de alta cobertura e integrando microsserviços.")
    elif strategy["domain"] == "FULLSTACK_JS":
        objetivo = (f"Atuar como Desenvolvedor(a) Full Stack Júnior na {company}, construindo interfaces modernas e acessíveis em React e TypeScript, "
                    f"integrando e mantendo APIs RESTful seguras e garantindo robustez e confiabilidade por meio de testes automatizados.")
    elif strategy["domain"] == "PYTHON_IA":
        objetivo = (f"Atuar como Desenvolvedor(a) Python e IA na {company}, desenvolvendo serviços backend escaláveis, "
                    f"integrando modelos de linguagem (LLMs) a fluxos reais de negócio e garantindo qualidade de código com testes automatizados e boas práticas de arquitetura.")
    elif strategy["domain"] == "CYBERSEC":
        objetivo = (f"Atuar na área de Cibersegurança / Pentest Júnior na {company}, identificando vulnerabilidades em sistemas web e APIs, "
                    f"conduzindo testes de intrusão e aplicando automações com Inteligência Artificial para segurança e conformidade de aplicações.")
    elif strategy["domain"] == "DADOS_RPA":
        objetivo = (f"Atuar como Analista / Desenvolvedor(a) de Dados e Automação Júnior na {company}, estruturando fluxos operacionais, "
                    f"construindo relatórios e dashboards com Python, SQL e Power BI e implementando automações digitais de processos.")
    else:
        objetivo = (f"Atuar como Desenvolvedor(a) de Software Júnior na {company}, construindo e mantendo serviços e APIs RESTful, "
                    f"otimizando consultas a bancos relacionais e colaborando ativamente na evolução técnica e arquitetural da plataforma.")

    # 2. Resumo sob medida
    if strategy["domain"] == "JAVA":
        resumo = (f"Estudante de Engenharia de Software (8º Período, PUCPR, conclusão 12/2026) com sólida base em Java e qualidade de software: "
                  f"no TCC realizo estudo empírico sobre arquitetura e testes em microsserviços Java/Spring Boot com JUnit 5, ArchUnit e mutation testing (Pitest). "
                  f"Experiência prática na construção de APIs REST, modelagem relacional SQL, Docker, pipelines de CI/CD e facilidade para evoluir em times ágeis.")
    elif strategy["domain"] == "FULLSTACK_JS":
        resumo = (f"Estudante de Engenharia de Software (8º Período, PUCPR, conclusão 12/2026) com vivência prática no desenvolvimento full stack: "
                  f"construí o Simulador de Trading com interfaces responsivas em React/TypeScript, gerenciamento de estados assíncronos e consumo de APIs REST, "
                  f"além de app em React Native e backend com CI/CD. Utilizo ferramentas de IA agêntica diariamente, revisando e testando com rigor todo código gerado.")
    elif strategy["domain"] == "PYTHON_IA":
        resumo = (f"Estudante de Engenharia de Software (8º Período, PUCPR, conclusão 12/2026) com Python como principal linguagem e foco em IA generativa: "
                  f"integrei a Gemini API ao backend Flask do Perfora para análise de imagens e desenvolvi o ClearBox para triagem inteligente de e-mails com LLMs. "
                  f"Domínio de testes automatizados (pytest, SonarCloud), autenticação segura JWT, bancos SQL relacionais e princípios de segurança da informação.")
    elif strategy["domain"] == "CYBERSEC":
        resumo = (f"Estudante de Engenharia de Software (8º Período, PUCPR) com certificações Cisco em Cibersegurança Júnior (2026), Segurança de Endpoint (2024) e Python. "
                  f"Desenvolvi sistemas com foco em segurança (autenticação JWT, hash bcrypt, proteção contra SQL injection e logs de auditoria) "
                  f"e integro IA generativa na automação de testes ofensivos e análise de vulnerabilidades. Inglês avançado para relatórios e leitura de CVEs.")
    elif strategy["domain"] == "DADOS_RPA":
        resumo = (f"Estudante de Engenharia de Software (8º Período, PUCPR) com forte perfil analítico e experiência prática em dados e processos: "
                  f"atuei em estágio multinacional (Oregon Tool) com automação de relatórios usando Python, SQL e Power BI, e em projeto de extensão com a Copel "
                  f"conduzindo mapeamento de processos (MPS.BR) e proposta de automações. Domínio de lógica, modelagem de dados e atenção a métricas de negócio.")
    else:
        resumo = (f"Estudante de Engenharia de Software (8º Período, PUCPR, conclusão 12/2026) com sólida base prática em desenvolvimento de software: "
                  f"construí serviços em camadas com APIs REST, autenticação segura, modelagem relacional SQL e testes automatizados com quality gate em CI/CD. "
                  f"Programo com suporte de IA agêntica no dia a dia, validando e testando criticamente cada implementação entregue.")

    # 3. Dicas e instruções para o portal
    dicas_portal = []
    if "gupy" in url.lower():
        dicas_portal.append("- Dica Gupy: Faça upload do PDF gerado nesta pasta e revise se o formulário puxou corretamente seus projetos e experiências.")
        dicas_portal.append(f"- Destaques recomendados no perfil Gupy: Fixe {strategy['pitch_focus']}.")
    elif "inhire" in url.lower():
        dicas_portal.append("- Dica Inhire: Envie o PDF gerado nesta pasta e adicione o link do GitHub (github.com/claudioc0).")
    elif "github.com" in url.lower():
        dicas_portal.append("- Dica GitHub: Verifique na issue se a candidatura é por e-mail ou link externo.")
    elif "programathor" in url.lower():
        dicas_portal.append("- Dica Programathor: Aplique pelo portal mantendo o perfil alinhado aos projetos citados.")
    elif "indeed" in url.lower():
        dicas_portal.append("- Dica Indeed: Utilize o PDF gerado nesta pasta para 'Candidatar-se pelo site da empresa' ou submeter pelo formulário Indeed.")

    dicas_str = "\n".join(dicas_portal) if dicas_portal else "- Envie o PDF gerado nesta pasta e revise os campos antes de submeter."

    # 4. Roteiro de Respostas (respostas.md)
    respostas = f"""# {company} – {title} ({modality})
Link: {url}

## Dados Pessoais e Contato
- Nome: Claudio Colombo Ferreira
- Email: claudiocolomboferreira13@gmail.com
- Telefone / WhatsApp: (41) 98811-5804
- LinkedIn: https://www.linkedin.com/in/claudio-colombo-ferreira
- GitHub: https://github.com/claudioc0
- Localização: Pinhais – PR (Região Metropolitana de Curitiba)
- Currículo em PDF: Curriculo_Claudio_Colombo.pdf (gerado nesta pasta)

## Condições e Pretensão
- Modalidade: {location} ({modality})
- Pretensão Salarial: R$ 3.500 a R$ 4.500 CLT (ou R$ 4.500 a R$ 6.000 PJ), negociável conforme benefícios e modelo de contratação
- Formação: Engenharia de Software (8º Período, PUCPR – previsão de conclusão 12/2026)

## Mensagem de Apresentação / Pitch Rápido
"Olá! Sou estudante do 8º período de Engenharia de Software na PUCPR e me candidatei à vaga de {title} na {company}. Tenho forte vivência prática com {strategy['role_focus']}, tendo desenvolvido projetos reais como {strategy['pitch_focus']}. Valorizo código testado, boas práticas de segurança e aprendo stacks novas com muita agilidade. Meu portfólio completo está em github.com/claudioc0 e estou à disposição para batermos um papo!"

## Instruções de Aplicação
{dicas_str}
"""

    return {
        "titulo": title,
        "empresa": company,
        "objetivo": objetivo,
        "resumo": resumo,
        "projetos": strategy["projetos"],
        "skill_cs": strategy["skill_cs"],
        "respostas": respostas
    }


def append_to_vagas_busca5(slug, package):
    """Registra a nova vaga em vagas_busca5.py para persistência no ecossistema."""
    arquivo = BASE_DIR / "vagas_busca5.py"
    if not arquivo.exists():
        conteudo_inicial = '''"""Vagas geradas dinamicamente via adicionar_vaga.py.
Importado dinamicamente no vagas.py.
"""
from vagas_busca1 import PERFORA, CLEARBOX, TRADING, TRADING_BACK, _resp
from vagas_busca3 import TCC
from vagas_busca4 import SEGURANCA_SW, OREGON_TOOL
from vagas_busca2 import NOVAS2

COPEL = (
    "Mapeamento de Processos e Automações Digitais (PUCPR / Copel) - Conclusão: 2025",
    "Análise e modelagem de processos de negócio de distribuidora de energia (Copel) via MPS.BR. Condução de gap analysis e proposição de automações digitais para eliminação de tarefas manuais e repetitivas."
)

NOVAS5 = {}
'''
        arquivo.write_text(conteudo_inicial, encoding="utf-8")

    # Mapear variáveis de projetos
    proj_map = {
        PERFORA[0]: "PERFORA",
        CLEARBOX[0]: "CLEARBOX",
        TRADING[0]: "TRADING",
        TRADING_BACK[0]: "TRADING_BACK",
        TCC[0]: "TCC",
        SEGURANCA_SW[0]: "SEGURANCA_SW",
        OREGON_TOOL[0]: "OREGON_TOOL",
        COPEL[0]: "COPEL"
    }

    p1_var = proj_map.get(package["projetos"][0][0], "PERFORA")
    p2_var = proj_map.get(package["projetos"][1][0], "TRADING")

    bloco = f'''
NOVAS5["{slug}"] = dict(
    objetivo={repr(package["objetivo"])},
    resumo={repr(package["resumo"])},
    projetos=[{p1_var}, {p2_var}],
    skill_cs={repr(package["skill_cs"])},
    respostas={repr(package["respostas"])}
)
'''
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(bloco)


def listar_vagas_radar():
    """Exibe as top novas vagas do arquivo radar."""
    if not BUSCA_JSON.exists():
        print("Arquivo de radar não encontrado. Execute 'python buscar_novas_vagas.py' primeiro.")
        return []

    with open(BUSCA_JSON, encoding="utf-8") as f:
        data = json.load(f)

    novas = [v for v in data if not v.get("ja_rastreada")]
    print("\n" + "=" * 70)
    print(f"TOP NOVAS VAGAS DISPONÍVEIS NO RADAR ({len(novas)} no total):")
    print("=" * 70)
    for i, v in enumerate(novas[:20], 1):
        print(f"[{i:2d}] [{v.get('fit_score', 0)}%] {v['title']} @ {v['company']} ({v.get('source', '')})")
        print(f"     Modalidade: {v.get('location', '')} ({v.get('modality', '')})")
        print(f"     URL: {v['url']}\n")
    print("=" * 70)
    print("Para gerar qualquer uma, execute: python adicionar_vaga.py <NUMERO>")
    print("Exemplo: python adicionar_vaga.py 1\n")
    return novas


def main():
    parser = argparse.ArgumentParser(description="Adiciona e gera candidatura completa com CV em PDF customizado.")
    parser.add_argument("alvo", nargs="?", default=None, help="Número da vaga no radar (ex: 1) ou URL da vaga")
    parser.add_argument("--list", action="store_true", help="Lista as principais vagas novas do radar")
    parser.add_argument("--manual", action="store_true", help="Cadastra vaga inserindo os dados manualmente")
    args = parser.parse_args()

    if args.list or (not args.alvo and not args.manual):
        listar_vagas_radar()
        return

    vaga_info = None

    if args.manual:
        print("\n--- CADASTRO MANUAL DE VAGA ---")
        title = input("Título da Vaga: ").strip()
        company = input("Nome da Empresa: ").strip()
        url = input("Link da Vaga: ").strip()
        modality = input("Modalidade (Remoto / Híbrido / Presencial) [Remoto]: ").strip() or "Remoto"
        location = input("Localização (ex: Curitiba / PR ou Remoto) [Brasil (Remoto)]: ").strip() or "Brasil (Remoto)"
        desc = input("Descrição ou requisitos resumidos: ").strip()
        vaga_info = {
            "title": title,
            "company": company,
            "url": url,
            "modality": modality,
            "location": location,
            "description": desc,
            "source": "Manual"
        }
    elif args.alvo.isdigit():
        num = int(args.alvo)
        if not BUSCA_JSON.exists():
            print("Erro: Arquivo do radar não encontrado.")
            return
        with open(BUSCA_JSON, encoding="utf-8") as f:
            data = json.load(f)
        novas = [v for v in data if not v.get("ja_rastreada")]
        if num < 1 or num > len(novas):
            print(f"Erro: Número {num} inválido. Escolha entre 1 e {len(novas)}.")
            return
        vaga_info = novas[num - 1]
    elif args.alvo.startswith("http"):
        # Tenta achar no radar
        url_target = args.alvo.strip()
        if BUSCA_JSON.exists():
            with open(BUSCA_JSON, encoding="utf-8") as f:
                data = json.load(f)
            for v in data:
                if v.get("url") == url_target or url_target in v.get("url", ""):
                    vaga_info = v
                    break
        if not vaga_info:
            print(f"URL externa não mapeada no radar: {url_target}")
            comp = input("Nome da empresa: ").strip()
            tit = input("Título da vaga: ").strip()
            vaga_info = {
                "title": tit,
                "company": comp,
                "url": url_target,
                "modality": "Remoto",
                "location": "Brasil (100% Remoto)",
                "description": "",
                "source": "Link Externo"
            }

    if not vaga_info:
        print("Erro: Não foi possível obter os dados da vaga.")
        return

    company = vaga_info.get("company", "Empresa")
    title = vaga_info.get("title", "Desenvolvedor")
    slug = get_next_slug(company, title)

    print("\n" + "=" * 70)
    print(f"CONFIGURANDO CANDIDATURA: {title} @ {company}")
    print(f"Slug gerado: {slug}")
    print("=" * 70)

    # Constrói o pacote adaptado
    package = build_candidate_package(vaga_info)

    print(f"\n[1/3] Estratégia selecionada:")
    print(f"  - Skill: {package['skill_cs']}")
    print(f"  - Projeto 1: {package['projetos'][0][0][:60]}...")
    print(f"  - Projeto 2: {package['projetos'][1][0][:60]}...")
    print(f"  - Objetivo: {package['objetivo'][:100]}...")

    print("\n[2/3] Registrando no ecossistema (vagas_busca5.py)...")
    append_to_vagas_busca5(slug, package)

    print("\n[3/3] Compilando Currículo PowerPoint e exportando PDF...")
    try:
        from gerar_cvs import gerar
        gerar(slug, package)
    except Exception as e:
        print(f"Aviso durante geração via PowerPoint COM: {e}")
        # Salva respostas.md mesmo se o COM falhar
        pasta = BASE_DIR / slug
        pasta.mkdir(exist_ok=True)
        (pasta / "respostas.md").write_text(package["respostas"].strip() + "\n", encoding="utf-8")

    pasta_final = BASE_DIR / slug
    print("\n" + "=" * 70)
    print(f"✅ CANDIDATURA GERADA COM SUCESSO!")
    print(f"Pasta: {pasta_final.resolve()}")
    print(f"Arquivos criados:")
    print(f"  - {pasta_final / 'Curriculo_Claudio_Colombo.pdf'}")
    print(f"  - {pasta_final / 'Curriculo_Claudio_Colombo.pptx'}")
    print(f"  - {pasta_final / 'respostas.md'}")
    print("=" * 70)

    # Exibe resumo do respostas.md
    print("\nPRÉVIA DO ROTEIRO DE RESPOSTAS (respostas.md):")
    print("-" * 50)
    for line in package["respostas"].splitlines()[:18]:
        print(line)
    print("...\n" + "=" * 70)


if __name__ == "__main__":
    main()
