# 🚀 Vagas-Go: Rastreador Concorrente de Vagas Tech & Gestor de Oportunidades

Sistema de alta performance desenvolvido em **Go** para descoberta paralela, filtragem estrita (*Fit Score*) e gerenciamento de vagas de desenvolvimento em banco de dados local **SQLite (embutido e sem necessidade de CGO)**.

---

## ⚡ Performance: Python vs Go

| Métrica | Python Legado (`buscar_novas_vagas.py`) | **Vagas-Go** (`vagas.exe`) |
| :--- | :--- | :--- |
| **Tempo de Execução** | ~3 a 5 minutos (execução sequencial) | **~4.0 segundos** (Fan-out / Fan-in concorrente) |
| **Dependências** | Python 3, venv, dezenas de bibliotecas pip | **Binário único nativo** (`vagas.exe`, 0 dependências) |
| **Concorrência** | `requests` síncrono e laços em série | **Goroutines + Channels + errgroup** |
| **Persistência** | Arquivos JSON planos e pastas | **Banco SQLite relacional** com índices otimizados |
| **Interface** | Scripts CLI avulsos | **CLI moderna (Cobra) + TUI interativa (Bubbletea)** |

---

## 🛠️ Comandos Disponíveis

### 1. Varredura Concorrente (`scan`)
Dispara as fontes em paralelo (APIs e múltiplos repositórios do GitHub), calcula os scores e insere no banco:
```powershell
.\vagas.exe scan
```

### 2. Interface Interativa de Terminal (`tui`)
Abre a interface interativa com tabela, detalhes e atalhos de teclado:
```powershell
.\vagas.exe tui
```
- **Navegação:** `↑` / `↓` ou `k` / `j`
- **Abrir link:** `Enter` (abre diretamente no navegador padrão)
- **Sair:** `q` ou `Esc`

### 3. Listagem Filtrada (`list`)
Exibe as melhores vagas no terminal com filtros rápidos:
```powershell
# Listar apenas vagas com Fit Score >= 80%
.\vagas.exe list -s 80

# Filtrar por vagas remotas com palavra-chave
.\vagas.exe list -m Remoto -q "Go"
```

### 4. Estatísticas do Banco (`stats`)
Exibe o volume total de vagas, contagem de elegíveis e taxa de conversão:
```powershell
.\vagas.exe stats
```

---

## 📁 Estrutura do Projeto

```text
vagas-go/
├── cmd/
│   └── vagas/main.go            # Ponto de entrada CLI (Cobra)
├── internal/
│   ├── domain/models.go         # Modelos Job, Source, Application
│   ├── pipeline/engine.go       # Fan-in/Fan-out concorrente
│   ├── provider/                # Scrapers e clientes de API
│   │   ├── provider.go          # Interface unificada
│   │   ├── github.go            # 11 Repositórios do GitHub em paralelo
│   │   └── remotar.go           # API Remotar com paginação
│   ├── storage/sqlite.go        # Driver SQLite puro (modernc.org/sqlite)
│   └── ui/tui/app.go            # Terminal UI rica (Bubbletea + Lipgloss)
├── pkg/
│   └── fitscore/scorer.go       # Algoritmo determinístico de Fit Score
├── go.mod
└── go.sum
```
