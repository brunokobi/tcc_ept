"""Descriptive figures for the paper and data for the advisor's page.

Uses only results that are already public in docs/resultados and the processed index panel.
Outcomes (evasao, conclusao) are dropped on load: nothing here may relate outcomes to Q, S or B
before the OSF pre-registration.

Usage: python scripts/make_figures.py
Outputs: reports/figures/*.png|svg and reports/figures/pagina_dados.json.
"""

from __future__ import annotations

import json
import math
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.ticker import FuncFormatter, ScalarFormatter

from tcc_aderencia.index.aderencia import linked_employment

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "docs" / "resultados"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "reports" / "figures"
GEO = ROOT / "data" / "external" / "ibge_rgi_malha.geojson"
GEO_URL = (
    "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?intrarregiao=regiao-imediata"
    "&formato=application/vnd.geo%2Bjson&qualidade=minima"
)
MAP_YEAR = 2021
MAP_COURSES = [
    "Técnico em Agropecuária",
    "Técnico em Informática",
    "Técnico em Enfermagem",
    "Técnico em Mineração",
    "Técnico em Petróleo e Gás",
    "Técnico em Logística",
]
SEED = 20261120

# Reference palette (dataviz skill): blue, orange; diverging blue <-> red with gray midpoint.
BLUE, ORANGE, GRAY_TXT, MUTED = "#2a78d6", "#eb6834", "#52514e", "#8a8984"
NO_DATA = "#9a9993"
DIVERGING = ["#c23b3a", "#e37b7a", "#f2b9b8", "#f0efec", "#b7d3f6", "#5598e7", "#1c5cab"]
Q_BINS = [-2.0, -1.0, -0.5, -0.15, 0.15, 0.5, 1.0, 2.0]
METHOD_LABELS = {
    "tfidf": "TF-IDF (linha de base)",
    "embeddings": "Embeddings",
    "caminho_O": "Caminho O (CBO)",
    "nvidia/nemotron-3-ultra-550b-a55b:free": "Nemotron (2º LLM)",
    "llm_final": "T final (ERNIE)",
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": GRAY_TXT,
        "xtick.color": GRAY_TXT,
        "ytick.color": GRAY_TXT,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#e6e5e1",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def br(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def thousands(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def save(fig, name: str, exts=("png", "svg")) -> None:
    comma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "\u2212"))
    for ax in fig.axes:
        for axis, scale in ((ax.xaxis, ax.get_xscale()), (ax.yaxis, ax.get_yscale())):
            if scale == "linear" and isinstance(axis.get_major_formatter(), ScalarFormatter):
                axis.set_major_formatter(comma)
    for ext in exts:
        fig.savefig(OUT / f"{name}.{ext}")
    plt.close(fig)


def load_panel() -> pd.DataFrame:
    df = pd.read_parquet(PROC / "indices.parquet")
    return df.drop(columns=["evasao", "conclusao"])  # pre-registration guard


def load_geo() -> dict:
    if not GEO.exists():
        with urllib.request.urlopen(GEO_URL, timeout=120) as r:
            GEO.write_bytes(r.read())
    return json.loads(GEO.read_text())


def rings(geom: dict) -> list[list[list[float]]]:
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    return [p[0] for p in polys]  # outer rings only (holes are negligible at this scale)


def project(lon: float, lat: float) -> tuple[float, float]:
    return lon * math.cos(math.radians(-15)), lat


# --------------------------------------------------------------------------- figures


def fig_classifier(ev: dict) -> dict:
    rows = [
        {"metodo": METHOD_LABELS[k], "chave": k, **{m: ev["metodos"][k][m] for m in ("acuracia", "macro_f1")},
         "ic_inf": ev["metodos"][k]["ic95"][0], "ic_sup": ev["metodos"][k]["ic95"][1]}
        for k in METHOD_LABELS
    ]
    fig, ax = plt.subplots(figsize=(6.2, 2.6))
    for i, r in enumerate(rows):
        color = BLUE if r["chave"] == "llm_final" else (MUTED if i < 3 else "#86b6ef")
        ax.plot([r["ic_inf"], r["ic_sup"]], [i, i], color=color, lw=2, solid_capstyle="round")
        ax.plot(r["macro_f1"], i, "o", ms=7, color=color, mec="white", mew=1.5)
        ax.text(r["ic_sup"] + 0.015, i, f"{r['macro_f1']:.2f}".replace(".", ","), va="center",
                color=GRAY_TXT, fontsize=8)
    ax.set_yticks(range(len(rows)), [r["metodo"] for r in rows])
    ax.set_xlim(0.3, 1.0)
    ax.set_xlabel("Macro-F1 no teste (201 subclasses), IC 95% por bootstrap")
    ax.grid(axis="y", visible=False)
    save(fig, "fig1_classificador")

    axes = sorted((a for a in ev["por_eixo_llm_final"] if a["eixo"] not in ("micro", "macro")),
                  key=lambda r: r["f1"])
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.barh([a["eixo"] for a in axes], [a["f1"] for a in axes], color=BLUE, height=0.6)
    for i, a in enumerate(axes):
        ax.text(a["f1"] + 0.01, i, f"{a['f1']:.2f}  (n={a['suporte']})".replace(".", ","), va="center",
                fontsize=7.5, color=GRAY_TXT)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("F1 por eixo, T final, teste")
    ax.grid(axis="y", visible=False)
    save(fig, "fig2_f1_por_eixo")
    return {
        "metodos": rows,
        "por_eixo": [{k: a[k] for k in ("eixo", "precisao", "revocacao", "f1", "suporte")} for a in axes[::-1]],
        "alfa_inter_llm": ev["alfa_inter_llm_teste"],
        "consenso": ev["consenso_teste"],
    }


def map_values(panel: pd.DataFrame) -> pd.DataFrame:
    emp = pd.read_parquet(PROC / "emprego_rgi_subclasse.parquet")
    emp = emp[emp.ano == MAP_YEAR]
    m = pd.read_parquet(PROC / "map_cnae_curso.parquet")
    w = m[m.curso.isin(MAP_COURSES) & (m.w_T > 0)].rename(columns={"curso": "unidade", "w_T": "w"})
    ql = linked_employment(emp, w)
    ql["Q"] = np.log(ql.QL)
    offered = panel[panel.curso.isin(MAP_COURSES)].groupby("curso").territorio.unique()
    return ql[["territorio", "unidade", "Q"]], {c: sorted(map(str, v)) for c, v in offered.items()}


def fig_maps(geo: dict, ql: pd.DataFrame, offered: dict) -> dict:
    feats = geo["features"]
    codes = [f["properties"]["codarea"] for f in feats]
    cmap = ListedColormap(DIVERGING)
    cmap.set_bad(NO_DATA)
    norm = BoundaryNorm(Q_BINS, cmap.N, extend="neither")
    show = MAP_COURSES[:3]
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.9))
    for ax, course in zip(axs, show, strict=True):
        q = ql[ql.unidade == course].set_index("territorio").Q
        polys, vals = [], []
        for code, f in zip(codes, feats, strict=True):
            v = q.get(code, np.nan)
            for ring in rings(f["geometry"]):
                polys.append([project(*p) for p in ring])
                vals.append(np.clip(v, Q_BINS[0] + 1e-9, Q_BINS[-1] - 1e-9) if pd.notna(v) else np.nan)
        pc = PolyCollection(polys, cmap=cmap, norm=norm, edgecolor="white", linewidth=0.15)
        pc.set_array(np.ma.masked_invalid(vals))
        ax.add_collection(pc)
        ax.autoscale_view()
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(course.replace("Técnico em ", ""), fontsize=10, color="#0b0b0b")
    cb = fig.colorbar(pc, ax=axs, orientation="horizontal", fraction=0.05, pad=0.02, aspect=50,
                      ticks=Q_BINS)
    cb.set_label(f"Q = ln QL do emprego ligado ao curso, {MAP_YEAR} (0 = média nacional; "
                 "cinza-escuro = sem emprego ligado)", color=GRAY_TXT)
    cb.ax.set_xticklabels(["\u2264 \u22122", "\u22121", "\u22120,5", "\u22120,15", "0,15", "0,5", "1", "\u2265 2"])
    cb.outline.set_visible(False)
    save(fig, "fig3_mapa_q", exts=("png",))  # SVG of 510 polygons is ~4 MB

    # Page payload: projected, rounded paths and values per course.
    rgi = pd.read_csv(ROOT / "data" / "external" / "ibge_municipios_rgi.csv", dtype=str)
    names = (rgi.drop_duplicates("cod_rgi").assign(n=lambda x: x.nome_rgi + " (" + x.uf + ")")
             .set_index("cod_rgi").n.to_dict())
    paths = []
    for code, f in zip(codes, feats, strict=True):
        d = []
        for ring in rings(f["geometry"]):
            pts, last = [], None
            for lon, lat in ring:
                x, y = project(lon, lat)
                p = (round(x, 2), round(-y, 2))
                if p != last:
                    pts.append(p)
                    last = p
            if len(pts) >= 3:
                d.append("M" + "L".join(f"{x:g},{y:g}" for x, y in pts) + "Z")
        paths.append({"c": code, "n": names.get(code, code), "d": "".join(d)})
    values = {
        c: {t: round(float(v), 3) for t, v in ql[ql.unidade == c].set_index("territorio").Q.items()}
        for c in MAP_COURSES
    }
    return {"ano": MAP_YEAR, "cursos": MAP_COURSES, "paths": paths, "Q": values, "ofertado": offered,
            "bins": Q_BINS}


def fig_convergence(panel: pd.DataFrame, idx: dict) -> dict:
    d = panel.dropna(subset=["Q", "R2"])
    rho = idx["convergencia_T_O"]["ciclos_Q_T_x_Q_O"]["rho"]
    fig, ax = plt.subplots(figsize=(4.4, 4.0))
    hb = ax.hexbin(d.Q, d.R2, gridsize=45, extent=(-4, 4, -3, 3), mincnt=1, cmap="Blues", bins="log",
                   linewidths=0.1)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("Q pelo caminho T (texto, LLM)")
    ax.set_ylabel("Q pelo caminho O (ocupações CBO)")
    ax.set_title(f"Spearman {br(rho)} em {thousands(len(d))} ciclos", fontsize=9, color=GRAY_TXT)
    cb = fig.colorbar(hb, ax=ax, fraction=0.04)
    cb.set_label("ciclos por célula (log)", color=GRAY_TXT)
    cb.outline.set_visible(False)
    save(fig, "fig4_convergencia_t_o")
    s = d.sample(n=min(2500, len(d)), random_state=SEED)
    return {
        "rho": rho, "n": len(d),
        "rho_S": idx["convergencia_T_O"]["ciclos_S_T_x_S_O"]["rho"],
        "rho_mediana_curso": idx["convergencia_T_O"]["mediana_por_curso_2018"],
        "pontos": [[round(a, 3), round(b, 3), bool(e)] for a, b, e in zip(s.Q, s.R2, s.ead, strict=True)],
    }


def fig_distributions(panel: pd.DataFrame) -> dict:
    spec = {"Q": (-4, 4), "S": (-1, 1), "B": (-0.4, 0.4)}
    labels = {"Q": "Q (aderência estrutural)", "S": "S (choque de demanda)", "B": "B (Bartik)"}
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 2.7))
    out = {}
    for ax, (var, (lo, hi)) in zip(axs, spec.items(), strict=True):
        edges = np.linspace(lo, hi, 41)
        out[var] = {"edges": [round(e, 4) for e in edges], "series": {}}
        for ead, color, name in ((False, BLUE, "Presencial"), (True, ORANGE, "EaD")):
            x = panel.loc[panel.ead == ead, var].dropna().clip(lo, hi)
            dens, _ = np.histogram(x, bins=edges, density=True)
            ax.stairs(dens, edges, color=color, lw=1.8, label=f"{name} (n={thousands(len(x))})")
            out[var]["series"][name] = {"dens": [round(float(v), 4) for v in dens], "n": len(x),
                                        "mediana": round(float(x.median()), 3)}
        ax.set_title(labels[var], fontsize=9.5, color="#0b0b0b")
        ax.set_yticks([])
        ax.grid(axis="y", visible=False)
    handles, names = axs[0].get_legend_handles_labels()
    fig.legend(handles, names, frameon=False, fontsize=8, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.1))
    fig.text(0.99, -0.1, "valores fora da janela somados nas pontas", ha="right", fontsize=7, color=MUTED)
    save(fig, "fig5_distribuicoes")
    return out


def coverage(panel: pd.DataFrame, idx: dict) -> dict:
    by = panel.groupby("ead").agg(ciclos=("ciclo_id", "size"), Q=("Q", lambda s: s.notna().mean()),
                                  S=("S", lambda s: s.notna().mean()), B=("B", lambda s: s.notna().mean()))
    return {
        "ciclos": idx["ciclos"], "ciclos_ead": idx["ciclos_ead"],
        "por_modalidade": {("EaD" if k else "Presencial"): {c: round(float(v), 4) for c, v in r.items()}
                           for k, r in by.iterrows()},
        "Q_nan_por_motivo": idx["cobertura"]["Q_nan_por_motivo"],
        "rho_S_B": idx["primeiro_estagio_descritivo_S_x_B"],
    }


def fig_sentinel(idx: dict) -> dict:
    s = idx["sentinelas"]["Agropecuaria_Q_medio_por_tercil_de_emprego_agro"]
    names = {"baixo": "Tercil baixo", "medio": "Tercil médio", "alto": "Tercil alto"}
    fig, ax = plt.subplots(figsize=(4.4, 2.4))
    vals = [s[k] for k in names]
    ax.bar(list(names.values()), vals, color=[DIVERGING[1], DIVERGING[4], DIVERGING[6]], width=0.55)
    ax.axhline(0, color=MUTED, lw=0.8)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.08 if v >= 0 else -0.08), f"{v:+.2f}".replace(".", ","), ha="center",
                va="bottom" if v >= 0 else "top", fontsize=8, color=GRAY_TXT)
    ax.set_ylabel("Q médio, Agropecuária")
    ax.set_xlabel("territórios por tercil do emprego agropecuário")
    ax.set_ylim(-1.6, 1.7)
    ax.grid(axis="x", visible=False)
    save(fig, "fig6_sentinela_agro")
    return s


def fig_prisma() -> dict:
    tri = pd.read_csv(ROOT / "docs" / "revisao" / "triagem.csv", dtype=str)
    inc = tri[tri.incluido.str.lower().isin(["sim", "true", "1", "s"])]
    cats = inc.categoria.value_counts().sort_index().to_dict()
    abstract = tri[tri.etapa != "título"]
    n = {"identificados": 478, "sem_duplicatas": len(tri), "excluidos_titulo": len(tri) - len(abstract),
         "resumos": len(abstract), "excluidos_resumo": len(abstract) - len(inc), "incluidos": len(inc),
         "categorias": cats}
    steps = [
        (f"Identificados na OpenAlex (4 strings)\nn = {n['identificados']}", None),
        (f"Após remover duplicatas\nn = {n['sem_duplicatas']}", f"Excluídos pelo título\nn = {n['excluidos_titulo']}"),
        (f"Resumos avaliados\nn = {n['resumos']}", f"Excluídos pelo resumo\nn = {n['excluidos_resumo']}"),
        ("Incluídos\nn = {}  ({})".format(n["incluidos"], ", ".join(f"{k} {v}" for k, v in cats.items())), None),
    ]
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(steps) * 2.2)
    for i, (main, side) in enumerate(steps):
        y = (len(steps) - i - 1) * 2.2 + 0.3
        ax.add_patch(plt.Rectangle((0.2, y), 5.2, 1.5, fc="#eef4fc", ec=BLUE, lw=1))
        ax.text(2.8, y + 0.75, main, ha="center", va="center", fontsize=8.5)
        if i < len(steps) - 1:
            ax.annotate("", xy=(2.8, y - 0.7), xytext=(2.8, y), arrowprops={"arrowstyle": "-|>", "color": MUTED})
        if side:
            ax.add_patch(plt.Rectangle((6.3, y + 0.15), 3.5, 1.2, fc="#f5f4f1", ec=MUTED, lw=0.8))
            ax.text(8.05, y + 0.75, side, ha="center", va="center", fontsize=8)
            ax.annotate("", xy=(6.3, y + 0.75), xytext=(5.4, y + 0.75),
                        arrowprops={"arrowstyle": "-|>", "color": MUTED})
    save(fig, "fig7_prisma")
    return n


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ev = json.loads((RES / "avaliacao-classificador-t.json").read_text())
    idx = json.loads((RES / "indices.json").read_text())
    panel = load_panel()
    geo = load_geo()
    ql, offered = map_values(panel)
    data = {
        "classificador": fig_classifier(ev),
        "mapa": fig_maps(geo, ql, offered),
        "convergencia": fig_convergence(panel, idx),
        "distribuicoes": fig_distributions(panel),
        "cobertura": coverage(panel, idx),
        "sentinela": fig_sentinel(idx),
        "prisma": fig_prisma(),
        "mde": {"H1a": {"evasao": 1.3, "conclusao": 1.6}, "H2": {"evasao": 7.5, "conclusao": 6.9}, "f": 0.38},
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (OUT / "pagina_dados.json").write_text(payload, encoding="utf-8")
    write_offline_page(payload)
    print("figuras em", OUT)


def write_offline_page(payload: str) -> None:
    """Self-contained copy of the advisor's page (data inlined) that opens straight from disk."""
    page = ROOT / "reports" / "pagina"
    html = (page / "index.html").read_text(encoding="utf-8")
    fetch = 'fetch("dados.json").then(r => r.json())'
    assert fetch in html
    html = html.replace(fetch, "Promise.resolve(DADOS)").replace(
        "<script>", "<script>\nconst DADOS = " + payload.replace("</", "<\\/") + ";\n", 1)
    if not html.lstrip().lower().startswith("<!doctype"):
        html = "<!doctype html>\n" + html
    (page / "pagina_offline.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
