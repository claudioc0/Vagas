"""Script para busca automatizada e ampliada de vagas em fontes qualificadas:
- Remotar (API de vagas 100% remotas no Brasil com paginação)
- GitHub Issues (11 repositórios brasileiros + GitHub Search API de vagas abertas)
- Gupy (Portal público com paginação dinâmica Next.js, vagas remotas e polo Curitiba/Paraná)
- Programathor (Startups e empresas de tecnologia com stack e senioridade)
- Trampos (API pública de vagas de tecnologia)
- Inhire (API REST multi-tenant direta de empresas e hubs tech no Brasil)
- Indeed Brasil (Scout automatizado via Playwright stealth para vagas remotas e polo Curitiba/PR)
- Nerdin (Portal de vagas tech no Brasil com filtros de júnior/estágio, home office e Curitiba)
- Vagas.com (Portal corporativo brasileiro com monitoramento de programador/dev júnior e Curitiba)
- Remotive (API pública global de vagas remotas de desenvolvimento abertas para Brasil/Worldwide)
- Remote OK (API pública de vagas remotas de engenharia e tecnologia)
- We Work Remotely (Feeds RSS com vagas de desenvolvimento remoto backend/frontend/fullstack)
- LinkedIn Alerts via Gmail IMAP (Leitura direta e imune a bloqueios de alertas oficiais do LinkedIn)

Aplica deduplicação cross-platform, filtro de elegibilidade estrito,
detecção de vagas já mapeadas nas pastas 01..27 e cálculo de Fit Score para o perfil de Claudio Colombo.
"""

import asyncio
import base64
import datetime
import email
import email.utils
import imaplib
import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from lxml import html

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "busca"
OUTPUT_DIR.mkdir(exist_ok=True)

# Carregamento simplificado e nativo de variáveis de ambiente do .env
def load_env_file(filepath=BASE_DIR / ".env"):
    if not filepath.exists():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception as e:
        print(f"  [Aviso] Falha ao carregar .env: {e}")

load_env_file()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
GH_HEADERS = {
    "User-Agent": "VagasScout/2.0",
    "Accept": "application/vnd.github.v3+json"
}

MAX_DIAS_RECENCIA = 15  # Filtro estrito: vagas com no máximo 15 dias de publicação


def parse_date(date_str):
    if not date_str:
        return datetime.date.today()
    try:
        clean = re.sub(r"[+-]\d{2}:\d{2}$", "", date_str.replace("Z", ""))
        return datetime.datetime.fromisoformat(clean).date()
    except Exception:
        return datetime.date.today()


def parse_indeed_relative_date(date_text):
    """Extrai data a partir do texto relativo de publicação do Indeed."""
    if not date_text:
        return datetime.date.today()
    txt = date_text.lower().strip()
    if any(k in txt for k in ["hoje", "recém", "just posted", "today", "recem"]):
        return datetime.date.today()
    if any(k in txt for k in ["ontem", "yesterday"]):
        return datetime.date.today() - datetime.timedelta(days=1)
    m = re.search(r"h[aá]\s+(\d+)\s+dia", txt)
    if m:
        days = int(m.group(1))
        return datetime.date.today() - datetime.timedelta(days=days)
    if "mais de 30" in txt or "30+" in txt:
        return datetime.date.today() - datetime.timedelta(days=31)
    m_en = re.search(r"(\d+)\+?\s+days?\s+ago", txt)
    if m_en:
        days = int(m_en.group(1))
        return datetime.date.today() - datetime.timedelta(days=days)
    return datetime.date.today()


def parse_nerdin_date(text):
    """Extrai data a partir do texto de publicação do Nerdin."""
    if not text:
        return datetime.date.today()
    t = text.lower().strip()
    if any(k in t for k in ["agora", "hoje", "minuto", "hora", "recent"]):
        return datetime.date.today()
    if "ontem" in t:
        return datetime.date.today() - datetime.timedelta(days=1)
    m = re.search(r"h[aá]\s+(\d+)\s+dia", t)
    if m:
        return datetime.date.today() - datetime.timedelta(days=int(m.group(1)))
    return datetime.date.today()


def parse_vagas_com_date(date_str):
    """Extrai data a partir de DD/MM/YYYY do Vagas.com."""
    if not date_str:
        return datetime.date.today()
    try:
        parts = date_str.strip().split("/")
        if len(parts) == 3:
            return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
    except Exception:
        pass
    return datetime.date.today()


def load_tracked_tokens():
    """Identifica tokens e URLs já presentes nas pastas 01..27 e em vagas*.py."""
    tokens = set()
    files = list(BASE_DIR.glob("**/respostas.md")) + list(BASE_DIR.glob("vagas*.py"))
    for f in files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
            for m in re.findall(r"https?://[^\s\)\"\']+", txt):
                clean = re.sub(r"[?&]utm_[^&]+", "", m).rstrip(".,;").lower()
                if len(clean) > 15:
                    tokens.add(clean)
                gupy_m = re.search(r"/job/([A-Za-z0-9+/=]+)", clean)
                if gupy_m:
                    tokens.add(gupy_m.group(1))
                inhire_m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", clean)
                if inhire_m:
                    tokens.add(inhire_m.group(1))
                indeed_m = re.search(r"jk=([a-zA-Z0-9]+)", clean)
                if indeed_m:
                    tokens.add(indeed_m.group(1))
                gh_m = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", clean)
                if gh_m:
                    tokens.add(f"{gh_m.group(1)}#{gh_m.group(2)}")
                nerdin_m = re.search(r"-(\d+)\.php", clean)
                if nerdin_m:
                    tokens.add(nerdin_m.group(1))
                vagascom_m = re.search(r"/vagas/(v\d+)/", clean)
                if vagascom_m:
                    tokens.add(vagascom_m.group(1))
        except Exception:
            pass
    return tokens


TRACKED_TOKENS = load_tracked_tokens()


def get_canonical_job_key(url, company, title):
    """Gera chave canônica para deduplicação entre fontes (ex: Remotar x Gupy)."""
    # Se for link base64 da Gupy
    m = re.search(r"/job/([A-Za-z0-9+/=]+)", url)
    if m:
        try:
            b64 = m.group(1)
            b64 += "=" * ((4 - len(b64) % 4) % 4)
            data = json.loads(base64.b64decode(b64).decode("utf-8"))
            jid = data.get("jobId")
            if jid:
                return f"gupy_id_{jid}"
        except Exception:
            pass

    # Se for Inhire (UUID)
    im = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", url)
    if im:
        return f"inhire_{im.group(1)}"

    # Se for Indeed
    ind_m = re.search(r"jk=([a-zA-Z0-9]+)", url)
    if ind_m:
        return f"indeed_{ind_m.group(1)}"

    # Se for GitHub issue
    ghm = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", url)
    if ghm:
        return f"gh_{ghm.group(1)}_{ghm.group(2)}"

    # Se for Programathor
    pm = re.search(r"/jobs/(\d+)", url)
    if pm:
        return f"pt_{pm.group(1)}"

    # Se for Nerdin
    nm = re.search(r"-(\d+)\.php", url)
    if nm and "nerdin" in url:
        return f"nerdin_{nm.group(1)}"

    # Se for Vagas.com.br
    vm = re.search(r"/vagas/(v\d+)/", url)
    if vm:
        return f"vagascom_{vm.group(1)}"

    # Se for Remotive
    rm = re.search(r"remotive\.com/.*?(\d+)", url)
    if rm:
        return f"remotive_{rm.group(1)}"

    # Chave por empresa + título simplificado
    norm_comp = re.sub(r"[^a-z0-9]", "", company.lower())
    norm_title = re.sub(r"[^a-z0-9]", "", title.lower())
    clean_url = re.sub(r"[?&].*$", "", url).rstrip("/")
    return f"{norm_comp}_{norm_title}_{clean_url}"


# =====================================================================
# 1. REMOTAR SCOUT (Com Paginação)
# =====================================================================
def fetch_remotar(seen_canonical):
    print("[1/10] Consultando Remotar (vagas 100% remotas com paginação)...")
    vagas = []
    queries = [
        "desenvolvedor junior",
        "desenvolvedor software jr",
        "trainee tecnologia",
        "python junior",
        "full stack junior",
        "front end junior",
        "back end junior",
        "java junior",
        "inteligencia artificial",
        "genai",
        "dados junior",
        "ciberseguranca"
    ]

    for q in queries:
        for page in [1, 2]:
            try:
                url = "https://api.remotar.com.br/jobs"
                resp = requests.get(url, params={"search": q, "limit": 20, "page": page}, headers=HEADERS, timeout=8)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                items = data.get("data", [])
                if not items:
                    break
                for item in items:
                    company = item.get("companyDisplayName")
                    if not company and isinstance(item.get("company"), dict):
                        company = item.get("company", {}).get("name")
                    company = (company or "Confidencial / Remotar").strip()

                    link = item.get("externalLink") or f"https://remotar.com.br/job/{item.get('id')}"
                    title = item.get("title", "").strip()

                    ckey = get_canonical_job_key(link, company, title)
                    if ckey in seen_canonical:
                        continue
                    seen_canonical.add(ckey)

                    created_at = item.get("createdAt")
                    pub_date = parse_date(created_at)
                    if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                        continue

                    vagas.append({
                        "id": f"remotar_{item.get('id')}",
                        "canonical_key": ckey,
                        "source": "Remotar",
                        "title": title,
                        "company": company,
                        "location": "Brasil (100% Remoto)",
                        "modality": "Remoto",
                        "url": link,
                        "published_date": str(pub_date),
                        "description": (item.get("description") or "")[:400]
                    })
            except Exception as e:
                print(f"  [Remotar] Erro na query '{q}' (pág {page}): {e}")

    print(f"  -> Remotar: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 2. GITHUB REPOS & SEARCH SCOUT
# =====================================================================
def fetch_github(seen_canonical):
    print("[2/10] Consultando repositórios e buscas no GitHub...")
    vagas = []
    repos = [
        "backend-br/vagas",
        "frontendbr/vagas",
        "react-brasil/vagas",
        "qa-brasil/vagas",
        "soujava/vagas-java",
        "androiddevbr/vagas",
        "flutterbr/vagas",
        "phpdevbr/vagas",
        "vuejs-br/vagas",
        "datascience-br/vagas",
        "DevOps-Brasil/Vagas"
    ]

    for repo in repos:
        try:
            url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=30"
            resp = requests.get(url, headers=GH_HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            issues = resp.json()
            for iss in issues:
                if iss.get("pull_request"):
                    continue
                pub_date = parse_date(iss.get("created_at"))
                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue
                url_iss = iss.get("html_url", "")
                title = iss.get("title", "").strip()
                company = repo.split("/")[0]

                ckey = get_canonical_job_key(url_iss, company, title)
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                labels = [l.get("name", "") for l in iss.get("labels", [])]
                labels_str = " ".join(labels)
                body = (iss.get("body") or "")[:500]

                modality = "Remoto" if ("remoto" in title.lower() or "remoto" in labels_str.lower()) else "Híbrido/Presencial"
                if "curitiba" in title.lower() or "curitiba" in body.lower():
                    location = "Curitiba / PR"
                elif modality == "Remoto":
                    location = "Remoto (Brasil)"
                else:
                    location = "Não especificado"

                vagas.append({
                    "id": f"gh_{repo}_{iss.get('number')}",
                    "canonical_key": ckey,
                    "source": f"GitHub ({company})",
                    "title": title,
                    "company": company,
                    "location": location,
                    "modality": modality,
                    "url": url_iss,
                    "published_date": str(pub_date),
                    "description": f"Labels: {', '.join(labels)} | {body[:250]}"
                })
        except Exception as e:
            print(f"  [GitHub] Erro no repo '{repo}': {e}")

    # GitHub Search API para buscar issues abertas com palavras-chave nos últimos 15 dias
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=MAX_DIAS_RECENCIA)).isoformat()
    search_queries = [
        f'is:open is:issue "junior" created:>={cutoff_date} repo:backend-br/vagas repo:frontendbr/vagas repo:soujava/vagas-java repo:react-brasil/vagas',
        f'is:open is:issue "Curitiba" created:>={cutoff_date} repo:backend-br/vagas repo:frontendbr/vagas repo:soujava/vagas-java'
    ]
    for sq in search_queries:
        try:
            resp = requests.get("https://api.github.com/search/issues", params={"q": sq, "per_page": 20}, headers=GH_HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            items = resp.json().get("items", [])
            for iss in items:
                pub_date = parse_date(iss.get("created_at"))
                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue
                repo_name = iss.get("repository_url", "").split("repos/")[-1]
                url_iss = iss.get("html_url", "")
                title = iss.get("title", "").strip()
                company = repo_name.split("/")[0] if repo_name else "GitHub"

                ckey = get_canonical_job_key(url_iss, company, title)
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                body = (iss.get("body") or "")[:500]
                modality = "Remoto" if "remoto" in title.lower() or "remoto" in body.lower() else "Híbrido/Presencial"
                location = "Curitiba / PR" if "curitiba" in title.lower() or "curitiba" in body.lower() else ("Remoto (Brasil)" if modality == "Remoto" else "Não especificado")

                vagas.append({
                    "id": f"gh_{repo_name}_{iss.get('number')}",
                    "canonical_key": ckey,
                    "source": f"GitHub ({company})",
                    "title": title,
                    "company": company,
                    "location": location,
                    "modality": modality,
                    "url": url_iss,
                    "published_date": str(pub_date),
                    "description": body[:250]
                })
        except Exception as e:
            print(f"  [GitHub Search] Erro na query '{sq}': {e}")

    print(f"  -> GitHub: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 3. GUPY SCOUT (Com Paginação Next.js e Parâmetros Ampliados)
# =====================================================================
def fetch_gupy(seen_canonical):
    print("[3/10] Consultando Gupy (Remoto + Polo Curitiba/PR com paginação Next.js)...")
    vagas = []
    gupy_queries = [
        "term=desenvolvedor%20junior",
        "term=programador%20junior",
        "term=desenvolvedor&state=Paran%C3%A1",
        "term=junior&state=Paran%C3%A1",
        "term=python%20junior",
        "term=full%20stack%20junior",
        "term=java%20junior",
        "term=ia",
        "term=dados%20junior",
        "term=trainee%20tecnologia"
    ]

    # Obter buildId do Next.js
    build_id = None
    try:
        resp = requests.get(f"https://portal.gupy.io/job-search/{gupy_queries[0]}", headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
            if m:
                d = json.loads(m.group(1))
                build_id = d.get("buildId")
    except Exception as e:
        print(f"  [Gupy] Erro ao obter buildId: {e}")

    for q in gupy_queries:
        # Página 1 (SSR)
        try:
            url = f"https://portal.gupy.io/job-search/{q}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
                if m:
                    data = json.loads(m.group(1))
                    items = data.get("props", {}).get("pageProps", {}).get("initialJobList", {}).get("data", [])
                    for it in items:
                        pub_date = parse_date(it.get("publishedDate"))
                        if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                            continue

                        title = it.get("name", "").strip()
                        company = it.get("careerPageName", "").strip()
                        job_url = it.get("jobUrl", "")

                        ckey = get_canonical_job_key(job_url, company, title)
                        if ckey in seen_canonical:
                            continue
                        seen_canonical.add(ckey)

                        wpt = it.get("workplaceType")
                        modality = "Remoto" if wpt == "remote" else ("Híbrido" if wpt == "hybrid" else "Presencial")
                        city = it.get("city") or ""
                        state = it.get("state") or ""
                        location = f"{city}, {state}".strip(", ") if (city or state) else modality

                        vagas.append({
                            "id": f"gupy_{it.get('id')}",
                            "canonical_key": ckey,
                            "source": "Gupy",
                            "title": title,
                            "company": company,
                            "location": location,
                            "modality": modality,
                            "url": job_url,
                            "published_date": str(pub_date),
                            "description": (it.get("description") or "")[:400]
                        })
        except Exception as e:
            print(f"  [Gupy] Erro na query '{q}': {e}")

        # Paginação via rota interna de dados Next.js (offset 12 e 24)
        if build_id:
            for offset in [12, 24]:
                try:
                    p_url = f"https://portal.gupy.io/_next/data/{build_id}/job-search/{q}.json?offset={offset}"
                    r_next = requests.get(p_url, headers=HEADERS, timeout=8)
                    if r_next.status_code == 200:
                        d_next = r_next.json()
                        items = d_next.get("pageProps", {}).get("initialJobList", {}).get("data", [])
                        for it in items:
                            pub_date = parse_date(it.get("publishedDate"))
                            if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                                continue

                            title = it.get("name", "").strip()
                            company = it.get("careerPageName", "").strip()
                            job_url = it.get("jobUrl", "")

                            ckey = get_canonical_job_key(job_url, company, title)
                            if ckey in seen_canonical:
                                continue
                            seen_canonical.add(ckey)

                            wpt = it.get("workplaceType")
                            modality = "Remoto" if wpt == "remote" else ("Híbrido" if wpt == "hybrid" else "Presencial")
                            city = it.get("city") or ""
                            state = it.get("state") or ""
                            location = f"{city}, {state}".strip(", ") if (city or state) else modality

                            vagas.append({
                                "id": f"gupy_{it.get('id')}",
                                "canonical_key": ckey,
                                "source": "Gupy",
                                "title": title,
                                "company": company,
                                "location": location,
                                "modality": modality,
                                "url": job_url,
                                "published_date": str(pub_date),
                                "description": (it.get("description") or "")[:400]
                            })
                except Exception:
                    pass

    print(f"  -> Gupy: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 4. PROGRAMATHOR SCOUT (Startups & Tech)
# =====================================================================
def fetch_programathor(seen_canonical):
    print("[4/10] Consultando Programathor (startups e empresas tech)...")
    vagas = []
    for page in [1, 2, 3]:
        try:
            url = f"https://programathor.com.br/jobs?page={page}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            tree = html.fromstring(resp.text)
            cards = tree.xpath("//div[contains(@class, 'cell-list')]")
            for card in cards:
                link_list = card.xpath(".//ancestor::a/@href") or card.xpath(".//a/@href")
                if not link_list:
                    continue
                link = link_list[0]
                if not link.startswith("/jobs/"):
                    continue

                title_list = card.xpath(".//h3//text()")
                title = title_list[0].strip() if title_list else ""
                if not title:
                    continue

                spans = [s.strip() for s in card.xpath(".//span//text()") if s.strip()]
                company = spans[0] if len(spans) > 0 else "Confidencial"
                full_url = f"https://programathor.com.br{link}"

                ckey = get_canonical_job_key(full_url, company, title)
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                modality = "Remoto" if any("remoto" in s.lower() for s in spans) else "Presencial/Híbrido"
                tags = spans[1:]
                desc = f"Empresa: {company} | Modalidade: {modality} | Tags: {', '.join(tags[:6])}"

                vagas.append({
                    "id": f"pt_{link.split('/')[-1]}",
                    "canonical_key": ckey,
                    "source": "Programathor",
                    "title": title,
                    "company": company,
                    "location": "Remoto (Brasil)" if modality == "Remoto" else "Brasil",
                    "modality": modality,
                    "url": full_url,
                    "published_date": str(datetime.date.today()),
                    "description": desc
                })
        except Exception as e:
            print(f"  [Programathor] Erro na página {page}: {e}")

    print(f"  -> Programathor: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 5. TRAMPOS SCOUT (API)
# =====================================================================
def fetch_trampos(seen_canonical):
    print("[5/10] Consultando Trampos.co (vagas de tecnologia)...")
    vagas = []
    for page in [1, 2]:
        try:
            url = "https://trampos.co/api/v2/opportunities"
            resp = requests.get(url, params={"page": page}, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            opps = resp.json().get("opportunities", [])
            for op in opps:
                title = op.get("name", "").strip()
                company_obj = op.get("company")
                company = company_obj.get("name") if isinstance(company_obj, dict) else op.get("custom_company_name") or "Confidencial"
                full_url = f"https://trampos.co/oportunidades/{op.get('id')}"

                ckey = get_canonical_job_key(full_url, company, title)
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                city = op.get("city") or ""
                state = op.get("state") or ""
                is_hybrid = op.get("hybrid", False)
                modality = "Remoto" if (not city and not state) or "remoto" in title.lower() else ("Híbrido" if is_hybrid else "Presencial")
                location = f"{city}, {state}".strip(", ") if (city or state) else modality

                pub_date = parse_date(op.get("published_at"))
                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue
                desc = f"Categoria: {op.get('category_name', '')} | Salário: {op.get('salary', 'Não informado')}"

                vagas.append({
                    "id": f"trampos_{op.get('id')}",
                    "canonical_key": ckey,
                    "source": "Trampos",
                    "title": title,
                    "company": company,
                    "location": location,
                    "modality": modality,
                    "url": full_url,
                    "published_date": str(pub_date),
                    "description": desc
                })
        except Exception as e:
            print(f"  [Trampos] Erro na página {page}: {e}")

    print(f"  -> Trampos: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 6. INHIRE SCOUT (API Direta Multi-Tenant de Empresas Tech)
# =====================================================================
def fetch_inhire(seen_canonical):
    print("[6/10] Consultando Inhire (API direta de ecossistemas e empresas tech)...")
    vagas = []
    tenants = [
        ("it4us-trial", "It4us Cyber Security"),
        ("yandeh", "Yandeh"),
        ("byx", "byx"),
        ("way2", "Way2"),
        ("vonbz", "VONBZ"),
        ("jump", "Jump"),
        ("clinicaexperts", "Clínica Experts"),
        ("mjv", "MJV Technology & Innovation"),
        ("deepesg", "DeepESG"),
        ("radix", "Radix"),
        ("pitang", "Pitang"),
        ("gx2", "GX2"),
        ("appmax", "Appmax"),
        ("programmers", "Programmers"),
        ("techlead", "Techlead IT Solutions"),
        ("unitech", "Unitech"),
        ("solutis", "Solutis"),
        ("dock", "Dock"),
        ("safetech", "Safetech"),
        ("takeblip", "Take Blip"),
        ("navita", "Navita"),
        ("tegra", "Tegra"),
        ("vindi", "Vindi")
    ]

    for tenant_id, default_comp in tenants:
        try:
            url = "https://api.inhire.app/job-posts/public/pages"
            resp = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "X-Tenant": tenant_id
            }, timeout=6)
            if resp.status_code != 200:
                continue
            data = resp.json()
            comp_name = data.get("tenantName") or default_comp
            items = data.get("jobsPage", [])
            for item in items:
                status = (item.get("status") or "").lower()
                if status and status != "published":
                    continue

                title = (item.get("displayName") or item.get("title") or "").strip()
                if not title:
                    continue

                job_id = item.get("jobId") or item.get("id")
                if not job_id:
                    continue

                job_url = f"https://{tenant_id}.inhire.app/vagas/{job_id}"

                ckey = get_canonical_job_key(job_url, comp_name, title)
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                wpt = (item.get("workplaceType") or "").lower()
                modality = "Remoto" if "remote" in wpt else ("Híbrido" if "hybrid" in wpt else "Presencial")
                loc_raw = item.get("location") or ""
                location = "Remoto (Brasil)" if modality == "Remoto" else (f"{loc_raw} ({modality})" if loc_raw else modality)

                vagas.append({
                    "id": f"inhire_{tenant_id}_{job_id}",
                    "canonical_key": ckey,
                    "source": f"Inhire ({comp_name})",
                    "title": title,
                    "company": comp_name,
                    "location": location,
                    "modality": modality,
                    "url": job_url,
                    "published_date": str(datetime.date.today()),
                    "description": f"Empresa: {comp_name} | Modalidade: {modality} | Inhire ATS"
                })
        except Exception:
            pass

    print(f"  -> Inhire: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 7. INDEED BRASIL SCOUT (Playwright Stealth Remoto & Curitiba/PR)
# =====================================================================
def fetch_indeed(seen_canonical):
    print("[7/10] Consultando Indeed Brasil (busca remota e polo Curitiba/PR)...")
    vagas = []

    async def _scout_indeed():
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("  [Indeed] Playwright não instalado. Pulando Indeed.")
            return []

        search_urls = [
            "https://br.indeed.com/jobs?q=desenvolvedor+junior&l=Remoto&fromage=14",
            "https://br.indeed.com/jobs?q=programador+junior&l=Remoto&fromage=14",
            "https://br.indeed.com/jobs?q=junior&l=Curitiba%2C+PR&fromage=14",
            "https://br.indeed.com/jobs?q=dados+junior&l=Remoto&fromage=14",
            "https://br.indeed.com/jobs?q=inteligencia+artificial+junior&l=Remoto&fromage=14"
        ]

        results = []
        try:
            async with async_playwright() as p:
                try:
                    browser = await p.chromium.launch(
                        channel="chrome",
                        headless=True,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                    )
                except Exception:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                    )

                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="pt-BR"
                )
                page = await context.new_page()
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                for s_url in search_urls:
                    try:
                        await page.goto(s_url, timeout=20000, wait_until="domcontentloaded")
                        await page.wait_for_timeout(2000)

                        cards = await page.locator("div.cardOutline").all()
                        for card in cards:
                            title_el = card.locator("h2.jobTitle, a[data-jk]").first
                            if await title_el.count() == 0:
                                continue
                            title = (await title_el.inner_text()).strip()
                            if not title:
                                continue

                            company_el = card.locator("span[data-testid='company-name']").first
                            company = (await company_el.inner_text()).strip() if await company_el.count() > 0 else "Confidencial"

                            loc_el = card.locator("div[data-testid='text-location']").first
                            loc = (await loc_el.inner_text()).strip() if await loc_el.count() > 0 else "Remoto"

                            link_el = card.locator("a[data-jk]").first
                            jk = await link_el.get_attribute("data-jk") if await link_el.count() > 0 else ""
                            if not jk:
                                continue

                            link = f"https://br.indeed.com/viewjob?jk={jk}"

                            ckey = get_canonical_job_key(link, company, title)
                            if ckey in seen_canonical:
                                continue
                            seen_canonical.add(ckey)

                            date_el = card.locator("span[data-testid='myJobsStateDate'], span.date, span.css-10pe3me").first
                            date_txt = (await date_el.inner_text()).strip() if await date_el.count() > 0 else ""
                            pub_date = parse_indeed_relative_date(date_txt)
                            if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                                continue

                            desc_el = card.locator("div.job-snippet, table.jobCardShelfContainer").first
                            desc = (await desc_el.inner_text()).replace("\n", " ").strip() if await desc_el.count() > 0 else ""

                            modality = "Remoto" if ("remoto" in loc.lower() or "remoto" in title.lower() or "remoto" in s_url.lower()) else ("Híbrido" if "híbrido" in loc.lower() else "Presencial")

                            results.append({
                                "id": f"indeed_{jk}",
                                "canonical_key": ckey,
                                "source": "Indeed",
                                "title": title,
                                "company": company,
                                "location": loc,
                                "modality": modality,
                                "url": link,
                                "published_date": str(pub_date),
                                "description": desc[:300]
                            })
                    except Exception:
                        pass

                await browser.close()
        except Exception as e:
            print(f"  [Indeed] Erro durante scout Indeed: {e}")

        return results

    try:
        vagas = asyncio.run(_scout_indeed())
    except Exception as e:
        print(f"  [Indeed] Falha ao executar scout: {e}")

    print(f"  -> Indeed: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 8. NERDIN SCOUT (Portal Tech Especializado – Remoto & Curitiba/PR)
# =====================================================================
def fetch_nerdin(seen_canonical):
    print("[8/10] Consultando Nerdin (vagas tech, home office, estágio/júnior e polo Curitiba)...")
    vagas = []

    routes = [
        ("https://nerdin.com.br/vagas-estagio-junior.php", 3),
        ("https://nerdin.com.br/vagas-home-office.php", 2),
        ("https://nerdin.com.br/vagas.php?Termo=junior", 2),
        ("https://nerdin.com.br/vagas.php?Termo=desenvolvedor", 2),
        ("https://nerdin.com.br/vagas.php?Cidade=Curitiba", 1),
        ("https://nerdin.com.br/vagas-desenvolvedor-sistemas.php", 1),
        ("https://nerdin.com.br/vagas-area-dados.php", 1),
    ]

    for base_url, max_pages in routes:
        for page in range(1, max_pages + 1):
            sep = "&" if "?" in base_url else "?"
            page_param = f"{sep}pagina={page}" if page > 1 else ""
            url = f"{base_url}{page_param}"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=8)
                if resp.status_code != 200:
                    continue
                tree = html.fromstring(resp.text)
                cards = tree.xpath("//a[contains(@href, 'vaga_emprego/')]")
                for a in cards:
                    href = a.get("href")
                    if not href:
                        continue
                    full_url = href if href.startswith("http") else f"https://nerdin.com.br/{href.lstrip('/')}"
                    row = a.xpath("./ancestor::div[contains(@class, 'row')][1]")
                    if not row:
                        continue
                    row = row[0]

                    title_el = row.xpath(".//h3[contains(@class, 'vaga-titulo')]//text()")
                    title = title_el[0].strip() if title_el else ""
                    if not title:
                        continue

                    comp_el = row.xpath(".//span[contains(@class, 'vaga-empresa-nome')]//text()")
                    company = comp_el[0].strip() if comp_el else "Confidencial"

                    ckey = get_canonical_job_key(full_url, company, title)
                    if ckey in seen_canonical:
                        continue
                    seen_canonical.add(ckey)

                    resumo_el = row.xpath(".//p[contains(@class, 'vaga-resumo-linha')]//text()")
                    resumo = " ".join(resumo_el).strip()

                    time_el = row.xpath(".//time//text()")
                    time_txt = time_el[0].strip() if time_el else ""
                    pub_date = parse_nerdin_date(time_txt)
                    if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                        continue

                    # Localização e modalidade
                    spans = [s.strip() for s in row.xpath(".//span//text()") if s.strip()]
                    loc = "Remoto" if ("home office" in resumo.lower() or "remoto" in resumo.lower()) else "Brasil"
                    for s in spans:
                        if "•" in s and not any(x in s.lower() for x in ["clt", "pj", "junior", "estágio", "pleno", "sênior", "r$"]):
                            loc = s.replace("•", "-").strip()
                            break
                        elif any(c in s.lower() for c in ["curitiba", "são paulo", "home office", "remoto", "rio de janeiro", "belo horizonte"]):
                            loc = s
                            break

                    modality = "Remoto" if ("home office" in resumo.lower() or "home office" in loc.lower() or "remoto" in loc.lower() or "remoto" in title.lower()) else ("Híbrido" if "híbrido" in resumo.lower() or "híbrido" in loc.lower() else "Presencial")
                    if modality == "Remoto" and loc == "Brasil":
                        loc = "Remoto (Brasil)"

                    tags = [t.strip() for t in row.xpath(".//a[contains(@class, 'hashtag')]//text()")]
                    desc = f"{resumo} | Local: {loc} | Tags: {', '.join(tags[:6])}"

                    vaga_id_m = re.search(r"-(\d+)\.php", full_url)
                    vid = vaga_id_m.group(1) if vaga_id_m else ckey

                    vagas.append({
                        "id": f"nerdin_{vid}",
                        "canonical_key": ckey,
                        "source": "Nerdin",
                        "title": title,
                        "company": company,
                        "location": loc,
                        "modality": modality,
                        "url": full_url,
                        "published_date": str(pub_date),
                        "description": desc
                    })
            except Exception as e:
                print(f"  [Nerdin] Erro na rota '{url}': {e}")

    print(f"  -> Nerdin: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 9. VAGAS.COM SCOUT (Portal Corporativo – Desenvolvedor Jr & Curitiba)
# =====================================================================
def fetch_vagas_com(seen_canonical):
    print("[9/10] Consultando Vagas.com (desenvolvedor/programador júnior e Curitiba)...")
    vagas = []
    queries = [
        "vagas-de-desenvolvedor-junior",
        "vagas-de-programador-junior",
        "vagas-de-junior-em-curitiba",
        "vagas-de-python-junior",
        "vagas-de-ti-junior-remoto"
    ]

    for q in queries:
        try:
            url = f"https://www.vagas.com.br/{q}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            tree = html.fromstring(resp.text)
            cards = tree.xpath("//li[contains(@class, 'vaga')]")
            for c in cards:
                title_a = c.xpath(".//h2[contains(@class, 'cargo')]//a | .//a[contains(@class, 'link-detalhes-vaga')]")
                if not title_a:
                    continue
                title = "".join(title_a[0].xpath(".//text()")).strip()
                if not title:
                    continue
                href = title_a[0].get("href", "")
                full_url = href if href.startswith("http") else f"https://www.vagas.com.br{href}"

                comp_txt = "".join(c.xpath(".//span[contains(@class, 'empr')]//text()")).strip()
                company = comp_txt or "Confidencial"

                ckey = get_canonical_job_key(full_url, company, title)
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                loc = "".join(c.xpath(".//span[contains(@class, 'vaga-local')]//text()")).strip()
                desc = "".join(c.xpath(".//div[contains(@class, 'detalhes')]//text()")).strip()
                date_txt = "".join(c.xpath(".//span[contains(@class, 'data-publicacao')]//text()")).strip()
                pub_date = parse_vagas_com_date(date_txt)
                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue

                modality = "Remoto" if ("100% remoto" in desc.lower() or "remoto" in loc.lower() or "remoto" in title.lower() or "home office" in desc.lower()) else ("Híbrido" if "híbrido" in desc.lower() or "hibrido" in loc.lower() else "Presencial")
                if not loc:
                    loc = "Remoto (Brasil)" if modality == "Remoto" else "Brasil"

                v_id = re.search(r"/(v\d+)/", full_url)
                jid = v_id.group(1) if v_id else ckey

                vagas.append({
                    "id": f"vagascom_{jid}",
                    "canonical_key": ckey,
                    "source": "Vagas.com",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "modality": modality,
                    "url": full_url,
                    "published_date": str(pub_date),
                    "description": desc[:300]
                })
        except Exception as e:
            print(f"  [Vagas.com] Erro na query '{q}': {e}")

    print(f"  -> Vagas.com: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 10. REMOTIVE SCOUT (Vagas Remotas Globais Abertas para Brasil/LATAM)
# =====================================================================
def fetch_remotive(seen_canonical):
    print("[10/10] Consultando Remotive (vagas remotas internacionais abertas para Brasil/Worldwide)...")
    vagas = []
    categories = ["software-dev", "data", "qa"]
    for cat in categories:
        try:
            url = f"https://remotive.com/api/remote-jobs?category={cat}&limit=30"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            data = resp.json()
            items = data.get("jobs", [])
            for item in items:
                loc = item.get("candidate_required_location", "")
                loc_lower = loc.lower()
                # Apenas vagas que aceitam candidatos do Brasil / Worldwide / LATAM / Americas
                if not any(k in loc_lower for k in ["anywhere", "worldwide", "latin america", "latam", "brazil", "brasil", "americas"]):
                    continue

                pub_date = parse_date(item.get("publication_date"))
                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue

                title = item.get("title", "").strip()
                company = item.get("company_name", "Confidencial").strip()
                link = item.get("url", "")

                ckey = f"remotive_{item.get('id')}"
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                desc = re.sub(r"<[^>]+>", " ", item.get("description", ""))[:350]

                vagas.append({
                    "id": ckey,
                    "canonical_key": ckey,
                    "source": "Remotive",
                    "title": title,
                    "company": company,
                    "location": f"Remoto ({loc})",
                    "modality": "Remoto",
                    "url": link,
                    "published_date": str(pub_date),
                    "description": desc
                })
        except Exception as e:
            print(f"  [Remotive] Erro na categoria '{cat}': {e}")

    print(f"  -> Remotive: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 11. REMOTE OK SCOUT (Vagas Remotas Globais Abertas para Brasil/LATAM/Worldwide)
# =====================================================================
def fetch_remoteok(seen_canonical):
    print("[11/13] Consultando Remote OK (vagas remotas internacionais)...")
    vagas = []
    try:
        url = "https://remoteok.com/api"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            jobs = [j for j in data if isinstance(j, dict) and j.get("id")]
            for item in jobs:
                loc = item.get("location") or ""
                loc_lower = loc.lower()
                allowed_regions = ["worldwide", "anywhere", "brazil", "brasil", "latam", "latin america", "americas", "global", "south america"]
                if loc and not any(r in loc_lower for r in allowed_regions):
                    continue

                pub_date = parse_date(item.get("date"))
                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue

                title = item.get("position", "").strip()
                company = item.get("company", "Confidencial").strip()
                link = item.get("url", "")
                if not link:
                    link = f"https://remoteok.com/remote-jobs/{item.get('id')}"

                ckey = f"remoteok_{item.get('id')}"
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                desc = re.sub(r"<[^>]+>", " ", item.get("description", ""))[:350]

                vagas.append({
                    "id": ckey,
                    "canonical_key": ckey,
                    "source": "Remote OK",
                    "title": title,
                    "company": company,
                    "location": f"Remoto ({loc})" if loc else "Remoto (Worldwide)",
                    "modality": "Remoto",
                    "url": link,
                    "published_date": str(pub_date),
                    "description": desc
                })
    except Exception as e:
        print(f"  [Remote OK] Erro na consulta: {e}")

    print(f"  -> Remote OK: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 12. WE WORK REMOTELY SCOUT (RSS Feeds Tech Backend/Frontend/FullStack)
# =====================================================================
def fetch_weworkremotely(seen_canonical):
    print("[12/13] Consultando We Work Remotely (RSS feeds tech)...")
    vagas = []
    categories = [
        "remote-back-end-programming-jobs",
        "remote-front-end-programming-jobs",
        "remote-full-stack-programming-jobs"
    ]
    for cat in categories:
        try:
            url = f"https://weworkremotely.com/categories/{cat}.rss"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            for item in items:
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubDate")
                desc_elem = item.find("description")
                guid_elem = item.find("guid")

                full_title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                guid = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else link

                if not full_title or not link:
                    continue

                if ": " in full_title:
                    company, title = full_title.split(": ", 1)
                else:
                    company, title = "Confidencial", full_title

                pub_date = datetime.date.today()
                if pub_elem is not None and pub_elem.text:
                    try:
                        parsed_time = email.utils.parsedate_to_datetime(pub_elem.text)
                        pub_date = parsed_time.date()
                    except Exception:
                        pub_date = datetime.date.today()

                if (datetime.date.today() - pub_date).days > MAX_DIAS_RECENCIA:
                    continue

                ckey = f"wwr_{guid}"
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                desc_raw = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                desc = re.sub(r"<[^>]+>", " ", desc_raw)[:350]

                vagas.append({
                    "id": ckey,
                    "canonical_key": ckey,
                    "source": "We Work Remotely",
                    "title": title,
                    "company": company,
                    "location": "Remoto (Worldwide/Global)",
                    "modality": "Remoto",
                    "url": link,
                    "published_date": str(pub_date),
                    "description": desc
                })
        except Exception as e:
            print(f"  [We Work Remotely] Erro na categoria '{cat}': {e}")

    print(f"  -> We Work Remotely: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 13. LINKEDIN ALERTS SCOUT (Via Gmail IMAP)
# =====================================================================
def fetch_linkedin_gmail(seen_canonical):
    print("[13/13] Consultando Alertas do LinkedIn (via Gmail IMAP)...")
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_pass:
        print("  -> LinkedIn/Gmail: GMAIL_USER e GMAIL_APP_PASSWORD não configurados no .env (pulando consulta).")
        return []

    vagas = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_pass.replace(" ", ""))
        mail.select("INBOX", readonly=True)

        status, data = mail.search(None, '(FROM "jobalerts-noreply@linkedin.com")')
        if status != "OK" or not data[0]:
            mail.logout()
            print("  -> LinkedIn/Gmail: Nenhum e-mail de alerta do LinkedIn encontrado na caixa de entrada.")
            return []

        mail_ids = data[0].split()
        recent_ids = mail_ids[-20:]

        for m_id in reversed(recent_ids):
            st, msg_data = mail.fetch(m_id, "(RFC822)")
            if st != "OK" or not msg_data:
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            date_tuple = email.utils.parsedate_tz(msg.get("Date"))
            if date_tuple:
                msg_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).date()
            else:
                msg_date = datetime.date.today()

            if (datetime.date.today() - msg_date).days > MAX_DIAS_RECENCIA:
                continue

            html_content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                if msg.get_content_type() == "text/html":
                    html_content = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            if not html_content:
                continue

            link_pattern = re.findall(r'<a\b[^>]*href="([^"]*linkedin\.com/(?:comm/)?jobs/view/(\d+)[^"]*)"[^>]*>([\s\S]*?)</a>', html_content, re.IGNORECASE)

            jobs_in_msg = {}
            for full_href, job_id, inner_html in link_pattern:
                title = re.sub(r"<[^>]+>", "", inner_html).strip()
                title = re.sub(r"\s+", " ", title)
                if not title or len(title) < 4 or any(ign in title.lower() for ign in ["candidatar", "ver vaga", "visualizar", "linkedin", "saiba mais"]):
                    continue
                if job_id not in jobs_in_msg:
                    jobs_in_msg[job_id] = title

            for job_id, title in jobs_in_msg.items():
                canonical_job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                ckey = f"linkedin_alert_{job_id}"
                if ckey in seen_canonical:
                    continue
                seen_canonical.add(ckey)

                vagas.append({
                    "id": ckey,
                    "canonical_key": ckey,
                    "source": "LinkedIn (Alertas)",
                    "title": title,
                    "company": "Empresa via LinkedIn",
                    "location": "Remoto / Alerta Configurado",
                    "modality": "Remoto",
                    "url": canonical_job_url,
                    "published_date": str(msg_date),
                    "description": f"Vaga recomendada recebida através dos alertas inteligentes do LinkedIn (ID {job_id})."
                })

        mail.logout()
    except Exception as e:
        print(f"  [LinkedIn/Gmail] Erro ao consultar IMAP: {e}")

    print(f"  -> LinkedIn/Gmail: {len(vagas)} vagas encontradas.")
    return vagas


# =====================================================================
# 14. FILTRAGEM INTELIGENTE E FIT SCORE
# =====================================================================
def is_already_tracked(vaga):
    """Verifica se a URL ou identificador da vaga já foi mapeado nas pastas 01..27."""
    url = vaga.get("url", "").lower()
    clean_url = re.sub(r"[?&]utm_[^&]+", "", url).rstrip(".,;")

    # Verificar match de URL ou tokens
    for tu in TRACKED_TOKENS:
        if tu in clean_url or clean_url in tu:
            return True

    # Verificar se o token Gupy bate
    gm = re.search(r"/job/([A-Za-z0-9+/=]+)", url)
    if gm and gm.group(1).lower() in TRACKED_TOKENS:
        return True

    # Verificar se o ID Inhire bate
    im = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", url)
    if im and im.group(1).lower() in TRACKED_TOKENS:
        return True

    # Verificar se o token Indeed bate
    jm = re.search(r"jk=([a-zA-Z0-9]+)", url)
    if jm and jm.group(1).lower() in TRACKED_TOKENS:
        return True

    # Verificar se o token Nerdin bate
    nm = re.search(r"-(\d+)\.php", url)
    if nm and nm.group(1).lower() in TRACKED_TOKENS:
        return True

    # Verificar se o token Vagas.com bate
    vm = re.search(r"/vagas/(v\d+)/", url)
    if vm and vm.group(1).lower() in TRACKED_TOKENS:
        return True

    return False


def calcular_fit_score(vaga):
    """Calcula Fit Score (0 a 100) para o perfil de Claudio Colombo.
    Aplica filtros rigorosos: APENAS nível Júnior/Trainee e EXCLUSIVAMENTE Core Tech/Software/Dados.
    """
    title_lower = vaga['title'].lower()
    comp_lower = vaga['company'].lower()
    desc_lower = vaga.get('description', '').lower()
    url_lower = vaga.get('url', '').lower()
    loc = vaga.get("location", "").lower()
    mod = vaga.get("modality", "").lower()
    texto = f"{title_lower} {comp_lower} {desc_lower} {url_lower}"

    # --- 1. DESQUALIFICADOR DE SENIORIDADE (Elimina Pleno, Sênior, Especialista, etc.) ---
    disqualify_seniority = [
        r'\bpleno\b', r'\bpl\b', r'\bmid\b', r'\bmid-level\b',
        r'\bs[eê]nior\b', r'\bsr\b', r'\bsr\.\b', r'\blead\b',
        r'\bstaff\b', r'\bprincipal\b', r'\bespecialista\b',
        r'\bmaster\b', r'\bhead\b', r'\bgerente\b', r'\bdiretor\b',
        r'\bcoordenador(a)?\b'
    ]
    for pat in disqualify_seniority:
        if re.search(pat, title_lower):
            return 0, "Nível acima de Júnior (Pleno/Sênior/Lead/Especialista)"

    # --- 2. EXIGÊNCIA EXPLÍCITA DE NÍVEL JÚNIOR OU TRAINEE ---
    junior_pattern = r'\b(j[uú]nior|jr\b|jr\.|trainee|entry(\s+level)?)\b'
    is_jr = bool(re.search(junior_pattern, title_lower)) or bool(re.search(junior_pattern, desc_lower))
    if not is_jr:
        return 0, "Não é vaga explicitamente Júnior ou Trainee"

    # --- 3. NÃO PODE SER ESTÁGIO (Formando em 12/2026) ---
    if re.search(r'\b(est[aá]gio|estagi[aá]ri[oa]|internship|intern\b)\b', title_lower):
        if not re.search(r'\btrainee\b', title_lower):
            return 0, "Vaga de estágio (formando em 12/2026)"

    # --- 4. VAGAS AFIRMATIVAS / PCD EXCLUSIVAS (Verifica título, descrição e link) ---
    affirmative_patterns = [
        r'\bpcd\b', r'\(pcd\)', r'\[pcd\]', r'-pcd-', r'_pcd_',
        r'exclusiv[ao]\s+para\s+mulheres', r'afirmativ[ao]\s+para\s+mulheres',
        r'para\s+pessoas?\s+com\s+defici[eê]ncia',
        r'exclusiv[ao]\s+(pcd|para\s+pcd)'
    ]
    for pat in affirmative_patterns:
        if re.search(pat, texto):
            return 0, "Vaga afirmativa (PcD / Mulheres / Grupos minorizados)"

    # --- 5. DESQUALIFICADOR DE ÁREAS NÃO-CORE TECH (Operações, Setor Elétrico, Suporte, Processos, etc.) ---
    non_core_tech = [
        r'\bopera[cç][oõ]es\b', r'\boperacional\b', r'\bmedi[cç][aã]o\b', r'\bfaturamento\b',
        r'\bsetor\s+el[eé]trico\b', r'\bel[eé]tric[ao]\b', r'\beletrot[eé]cnic[ao]\b', r'\bsmf\b',
        r'\bsuporte\b', r'\bhelp\s*desk\b', r'\bservice\s*desk\b', r'\batendimento\b',
        r'\binfraestrutura\b', r'\bredes\b', r'\btelecom\b', r'\bt[eé]cnic[ao]\s+de\s+ti\b',
        r'\bt[eé]cnic[ao]\s+de\s+inform[aá]tica\b', r'\bprocessos\b', r'\bmelhoria\s+cont[ií]nua\b',
        r'\bpcm\b', r'\bmanuten[cç][aã]o\b', r'\bfacilities\b', r'\bmarketing\b', r'\bseo\b',
        r'\bm[ií]dia\b', r'\bgrowth\b', r'\btr[aá]fego\b', r'\bweb\s+analytics\b',
        r'\bcomercial\b', r'\bvendas\b', r'\bdesigner?\b', r'\bui/ux\b', r'\bux/ui\b',
        r'\bcontroladoria\b', r'\bcont[aá]bil\b', r'\bfiscal\b', r'\brecrutamento\b',
        r'\bprofessor\b', r'\bprofessora\b', r'\bingl[eê]s\b', r'\bqu[ií]mica\b', r'\bfarm[aá]cia\b'
    ]
    for pat in non_core_tech:
        if re.search(pat, title_lower):
            return 0, "Área não-core dev/tech (operações/suporte/elétrico/administrativo)"

    # --- 6. EXIGÊNCIA DE SER CORE TECH ROLE (Software, Dev, Dados, IA, Segurança, QA) ---
    core_tech_patterns = [
        r'\b(dev|desenvolvedor(a)?|developer|software|programador(a)?|engenheiro(a)?\s+de\s+software|engenharia\s+de\s+software)\b',
        r'\b(full\s*stack|front\s*end|frontend|back\s*end|backend|mobile|web)\b',
        r'\b(intelig[eê]ncia\s+artificial|\bia\b|ai\b|genai|llm|machine\s+learning|prompt)\b',
        r'\b(dados|data\s+engineer|engenheir[oa]\s+de\s+dados|cientista\s+de\s+dados|analista\s+de\s+dados|power\s*bi)\b',
        r'\b(qa|qualidade\s+de\s+software|testes?|test\s+engineer)\b',
        r'\b(ciberseguran[cç]a|cybersecurity|pentest(er)?|seguran[cç]a\s+da\s+informa[cç][aã]o|appsec)\b',
        r'\b(rpa|automa[cç][aã]o\s+de\s+software|python|java|react|typescript|node)\b'
    ]
    if not any(re.search(pat, title_lower) for pat in core_tech_patterns):
        return 0, "Título não corresponde a Core Tech/Software/Dados"

    # --- 7. LOCALIZAÇÃO INCOMPATÍVEL ---
    if mod in ["presencial", "híbrido"] or "on-site" in mod or "hybrid" in mod:
        is_curitiba = any(c in loc for c in ["curitiba", "pinhais", "são josé dos pinhais", "colombo", "araucária", "paran"])
        if not is_curitiba and any(c in loc for c in ["são paulo", "sp", "rio de janeiro", "rj", "belo horizonte", "bh", "salvador", "porto alegre", "blumenau", "recife", "campinas", "osasco", "londrina", "maringá"]):
            return 0, f"Localização incompatível ({vaga['location']})"

    # --- 8. FILTRO DE RECÊNCIA (Máximo de 15 dias atrás) ---
    pub_str = vaga.get("published_date")
    if pub_str:
        try:
            pub_date = datetime.date.fromisoformat(pub_str)
            dias_atras = (datetime.date.today() - pub_date).days
            if dias_atras > MAX_DIAS_RECENCIA:
                return 0, f"Publicada há mais de {MAX_DIAS_RECENCIA} dias ({dias_atras} dias atrás)"
        except Exception:
            pass

    # --- 9. PONTUAÇÃO DE FIT (Perfil Claudio Colombo) ---
    score = 30  # Base para vagas aprovadas estritas

    # Nível alvo (+25)
    if any(k in title_lower for k in ["júnior", "junior", "jr", "trainee", "entry level", "entry"]):
        score += 25

    # Modalidade (+20 a +25)
    if "remoto" in mod or "remoto" in loc:
        score += 20
    elif any(c in loc for c in ["curitiba", "pinhais", "são josé dos pinhais"]):
        score += 25  # Bônus concorrência menor

    # Tecnologias centrais do Claudio
    stack_weights = [
        (["ia", "inteligência artificial", "llm", "genai", "generative ai", "prompt", "claude", "cursor", "vibe"], 20),
        (["python", "flask", "fastapi", "django"], 15),
        (["react", "react native", "next.js", "nextjs"], 15),
        (["typescript", "javascript", "node", "nodejs"], 12),
        (["java", "spring", "spring boot", "springboot", "junit"], 15),
        (["cibersegurança", "cybersecurity", "pentest", "segurança", "owasp", "vulnerabilidade"], 15),
        (["sql", "sqlite", "mysql", "postgresql"], 8),
        (["power bi", "bi", "dados", "analytics", "rpa", "automação"], 10),
        (["testes", "pytest", "junit", "qualidade", "ci/cd", "docker", "archunit", "mutação"], 10),
    ]

    for keywords, points in stack_weights:
        if any(re.search(r"\b" + re.escape(kw) + r"\b", texto) for kw in keywords):
            score += points

    # Bônus de Recência
    try:
        pub = datetime.date.fromisoformat(vaga["published_date"])
        diff = (datetime.date.today() - pub).days
        if diff <= 3:
            score += 15
        elif diff <= 7:
            score += 10
        elif diff <= 15:
            score += 5
    except Exception:
        pass

    score = min(score, 100)
    return score, "Elegível Júnior Tech"


# =====================================================================
# 15. RECRUITER POSTS DIGEST & TELEGRAM NOTIFIER
# =====================================================================
def generate_recruiter_digest_md():
    """Gera bloco Markdown com buscas inteligentes de posts de tech recruiters nas últimas 24h."""
    queries = [
        ("Tech Recruiter buscando Dev Júnior (Remoto)", "contratando desenvolvedor júnior remoto"),
        ("Vagas e Estágios em Desenvolvimento (Remoto)", "vaga estágio desenvolvimento remoto"),
        ("Publicações com hashtag #vagajunior", '"#vagajunior" remoto'),
        ("Tech Recruiters buscando Dev Python / IA / Dados Jr", "contratando junior python remoto"),
        ("Tech Recruiters buscando Dev Full Stack / React / Node Jr", "contratando junior react node remoto"),
        ("Tech Recruiters buscando Dev Java / Spring Jr", "contratando junior java remoto"),
    ]
    lines = [
        "\n---\n",
        "## 📣 Radar de Publicações de Tech Recruiters no LinkedIn (Últimas 24h)\n",
        "> *Muitos recrutadores anunciam oportunidades de estágio e júnior diretamente em seus feeds pessoais antes de publicarem vagas corporativas. Clique nos links abaixo para abrir a busca em tempo real com filtro das últimas 24 horas:*\n"
    ]
    for label, q in queries:
        encoded_q = urllib.parse.quote(q)
        url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_q}&datePosted=%22past-24h%22&sortBy=%22date_posted%22"
        lines.append(f"- 🔎 **[{label}]({url})**")
    lines.append("")
    return "\n".join(lines)


def send_telegram_notifications(vagas_novas_top):
    """Envia alertas em tempo real das vagas quentes para o Telegram via Bot API."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("\nℹ️  Telegram Bot: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados no .env (alertas móveis desativados).")
        return

    if not vagas_novas_top:
        return

    print(f"\n📲 Enviando {len(vagas_novas_top)} alertas de vagas de altíssima relevância para o Telegram...")
    try:
        header = f"🎯 <b>Radar de Vagas: {len(vagas_novas_top)} Oportunidades Quentes (Score ≥ 80%)</b>\n\n"
        blocks = []
        for v in vagas_novas_top:
            block = (
                f"🔥 <b>[{v['fit_score']}%] {v['title']}</b>\n"
                f"🏢 <b>Empresa:</b> {v['company']}\n"
                f"📍 <b>Local:</b> {v['location']} ({v['modality']})\n"
                f"🏷 <b>Fonte:</b> {v['source']}\n"
                f"🔗 <a href='{v['url']}'>Acessar Vaga</a>\n"
            )
            blocks.append(block)

        msg_current = header
        for b in blocks:
            if len(msg_current) + len(b) + 2 > 3800:
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={"chat_id": chat_id, "text": msg_current, "parse_mode": "HTML", "disable_web_page_preview": True},
                    timeout=10
                )
                msg_current = ""
            msg_current += (b + "\n")

        if msg_current:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": msg_current, "parse_mode": "HTML", "disable_web_page_preview": True},
                timeout=10
            )
        print("  -> Notificações enviadas com sucesso para o Telegram!")
    except Exception as e:
        print(f"  [Telegram] Erro ao enviar notificação: {e}")


# =====================================================================
# 16. EXECUÇÃO PRINCIPAL E RELATÓRIO
# =====================================================================
def main():
    print("=" * 70)
    print("RADAR AMPLIADO DE VAGAS – Claudio Colombo Ferreira")
    print(f"Identificadores/URLs já rastreados no sistema: {len(TRACKED_TOKENS)}")
    print("=" * 70)

    seen_canonical = set()
    todas = []

    todas.extend(fetch_remotar(seen_canonical))
    todas.extend(fetch_github(seen_canonical))
    todas.extend(fetch_gupy(seen_canonical))
    todas.extend(fetch_programathor(seen_canonical))
    todas.extend(fetch_trampos(seen_canonical))
    todas.extend(fetch_inhire(seen_canonical))
    todas.extend(fetch_indeed(seen_canonical))
    todas.extend(fetch_nerdin(seen_canonical))
    todas.extend(fetch_vagas_com(seen_canonical))
    todas.extend(fetch_remotive(seen_canonical))
    todas.extend(fetch_remoteok(seen_canonical))
    todas.extend(fetch_weworkremotely(seen_canonical))
    todas.extend(fetch_linkedin_gmail(seen_canonical))

    print(f"\nTotal bruto único coletado em todas as 13 fontes: {len(todas)} vagas.")

    # Avaliação de Fit
    qualificadas = []
    descartadas_count = 0

    for v in todas:
        score, motivo = calcular_fit_score(v)
        v["fit_score"] = score
        v["motivo_status"] = motivo
        v["ja_rastreada"] = is_already_tracked(v)
        v["tag_status"] = "📌 MAPEADA" if v["ja_rastreada"] else "✨ NOVA"

        if score >= 50:
            qualificadas.append(v)
        else:
            descartadas_count += 1

    # Ordenar por Fit Score decrescente, priorizando NOVAS e datas recentes
    qualificadas.sort(key=lambda x: (not x["ja_rastreada"], x["fit_score"], x["published_date"]), reverse=True)

    novas_count = sum(1 for v in qualificadas if not v["ja_rastreada"])
    mapeadas_count = sum(1 for v in qualificadas if v["ja_rastreada"])

    print(f"Vagas qualificadas (Score >= 50): {len(qualificadas)} (✨ {novas_count} NOVAS | 📌 {mapeadas_count} já mapeadas)")
    print(f"Vagas descartadas por filtros: {descartadas_count}")

    # Salvar JSON consolidado (faz backup automático da rodada anterior)
    json_path = OUTPUT_DIR / "vagas_encontradas.json"
    anterior_path = OUTPUT_DIR / "vagas_encontradas_anterior.json"
    if json_path.exists():
        import shutil
        shutil.copy(json_path, anterior_path)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(qualificadas, f, indent=2, ensure_ascii=False)
    print(f"JSON salvo em: {json_path}")

    # Gerar Relatório Markdown
    md_path = OUTPUT_DIR / "radar_vagas_recomendadas.md"
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    md_lines = [
        f"# Radar Ampliado de Vagas Recomendadas (Últimos {MAX_DIAS_RECENCIA} dias) – {hoje}",
        f"\nTotal de oportunidades qualificadas encontradas: **{len(qualificadas)}** (✨ **{novas_count} novas** e 📌 **{mapeadas_count} já mapeadas** | Máx. {MAX_DIAS_RECENCIA} dias de publicação)\n",
        "| Status | Score | Título da Vaga | Empresa | Modalidade / Local | Fonte | Link |",
        "|:---:|:---:|---|---|---|---|:---:|"
    ]

    for v in qualificadas:
        link_md = f"[Acessar Vaga]({v['url']})"
        md_lines.append(f"| {v['tag_status']} | **{v['fit_score']}%** | {v['title']} | {v['company']} | {v['location']} ({v['modality']}) | {v['source']} | {link_md} |")

    md_lines.append("\n## Destaques de Altíssima Aderência (Score >= 75%)\n")
    top_picks = [v for v in qualificadas if v["fit_score"] >= 75 and not v["ja_rastreada"]]
    if not top_picks:
        top_picks = [v for v in qualificadas if not v["ja_rastreada"]][:5]
    if not top_picks:
        top_picks = qualificadas[:5]

    for v in top_picks:
        badge = "✨ NOVA OPORTUNIDADE" if not v["ja_rastreada"] else "📌 JÁ MAPEADA"
        md_lines.append(f"### 🎯 [{v['fit_score']}%] {v['title']} – {v['company']} ({badge})")
        md_lines.append(f"- **Modalidade/Local:** {v['location']} ({v['modality']})")
        md_lines.append(f"- **Data de Publicação:** {v['published_date']}")
        md_lines.append(f"- **Fonte:** {v['source']}")
        md_lines.append(f"- **Link:** {v['url']}")
        md_lines.append(f"- **Contexto:** {v.get('description', '')[:250]}...")
        md_lines.append("")

    # Adicionar seção de Digest de Tech Recruiters no LinkedIn
    md_lines.append(generate_recruiter_digest_md())

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Relatório Markdown gerado em: {md_path}")

    # Notificar via Telegram se configurado (para vagas inéditas quentes Score >= 80)
    vagas_para_telegram = [v for v in qualificadas if not v["ja_rastreada"] and v["fit_score"] >= 80][:15]
    send_telegram_notifications(vagas_para_telegram)

    # Exibir Top 10 NOVAS no console
    novas_top = [v for v in qualificadas if not v["ja_rastreada"]]
    print("\n" + "=" * 70)
    print(f"TOP 10 NOVAS VAGAS MAIS CONDIZENTES HOJE ({len(novas_top)} disponíveis):")
    print("=" * 70)
    for i, v in enumerate(novas_top[:10], 1):
        print(f"{i:2d}. [{v['fit_score']}%] {v['title']} @ {v['company']}")
        print(f"    Local: {v['location']} ({v['modality']}) | Fonte: {v['source']}")
        print(f"    URL: {v['url']}\n")


if __name__ == "__main__":
    main()
