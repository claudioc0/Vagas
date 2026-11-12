"""Gera currículos adaptados editando APENAS os textos do PPTX original (layout intacto) e exporta PDF via PowerPoint."""
import subprocess
from pathlib import Path

from pptx import Presentation

from vagas import VAGAS

BASE = Path(__file__).parent
MODELO = Path.home() / "Downloads" / "Curriculo_Claudio_Colombo_AuthSoft.pptx"
if not MODELO.exists():
    MODELO = Path(r"E:\backup-pc-20261014\Downloads\Curriculo_Claudio_Colombo_AuthSoft.pptx")


def achar(shapes, nome):
    for sh in shapes:
        if sh.shape_type == 6:  # grupo
            r = achar(sh.shapes, nome)
            if r is not None:
                return r
        elif sh.name == nome:
            return sh
    return None


def set_par(par, texto):
    """Troca o texto mantendo a formatação do primeiro run."""
    runs = par.runs
    runs[0].text = texto
    for r in runs[1:]:
        r.text = ""


def gerar(slug, v):
    prs = Presentation(MODELO)
    sl = prs.slides[0]
    ps = lambda nome: achar(sl.shapes, nome).text_frame.paragraphs

    set_par(ps("CaixaDeTexto 143")[0], v["objetivo"])
    set_par(ps("CaixaDeTexto 141")[0], v["resumo"])
    proj = ps("CaixaDeTexto 153")
    (t1, d1), (t2, d2) = v["projetos"]
    set_par(proj[0], t1); set_par(proj[1], d1)
    set_par(proj[3], t2); set_par(proj[4], " " + d2)
    if "skill_cs" in v:  # 6ª barra (7 bolinhas = intermediário)
        a, b = v["skill_cs"]
        p = ps("CaixaDeTexto 129")
        set_par(p[0], a + " "); set_par(p[1], "– " + b)

    pasta = BASE / slug
    pasta.mkdir(exist_ok=True)
    pptx = pasta / "Curriculo_Claudio_Colombo.pptx"
    prs.save(pptx)
    pdf = pptx.with_suffix(".pdf")
    ps_cmd = (f"$a=New-Object -ComObject PowerPoint.Application;"
              f"$p=$a.Presentations.Open('{pptx}',$true,$false,$false);"
              f"$p.SaveAs('{pdf}',32);$p.Close();$a.Quit()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
    (pasta / "respostas.md").write_text(v["respostas"].strip() + "\n", encoding="utf-8")
    for velho in ("curriculo.html",):
        (pasta / velho).unlink(missing_ok=True)
    print("ok", pdf)


if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(VAGAS.keys())
    for slug in targets:
        if slug in VAGAS:
            gerar(slug, VAGAS[slug])
        else:
            print(f"Aviso: vaga '{slug}' não encontrada.")
