"""Sorteio da amostra de referência CNAE → eixo (spec 02) e planilhas de anotação.

- Universo: 1.332 subclasses CNAE 2.3; peso = vínculos médios na RAIS 2019–2023 (harmonizada).
- Estratos: seção CNAE × faixa de emprego (terços nacionais: alto/médio/baixo).
- Alocação por seção: N × (½ participação no nº de subclasses + ½ participação no emprego),
  mínimo de 3 (ou a seção inteira, se menor); dentro da seção, igual entre as faixas presentes.
- Divisão dev (1/3) / teste (2/3), estratificada por seção, feita antes de qualquer classificador.
- Saídas: data/reference/gold_v1.csv (amostra + desenho, colunas de anotação vazias) e
  annotation/anotacao_avaliador_{A,B}.xlsx (lista suspensa com os eixos).

Uso: python scripts/sample_reference.py [N=300]
"""

from __future__ import annotations

import sys

import duckdb
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from tcc_aderencia.config import DATA, INTERIM, REFERENCE, ROOT, SEED
from tcc_aderencia.ingest.cnae import harmonize

YEARS = range(2019, 2024)
MIN_PER_SECTION = 3
DEV_SHARE = 1 / 3
NAO_SE_APLICA = "Não se aplica (nenhum curso técnico)"


def employment() -> pd.Series:
    files = [f"{INTERIM}/rais/{y}/*.parquet" for y in YEARS]
    df = duckdb.sql(
        f"select cnae_subclasse, sum(vinculos) vinculos from read_parquet({files}) group by 1"
    ).df()
    df = harmonize(df).groupby("cnae_subclasse").vinculos.sum() / len(YEARS)
    return df


def allocate(frame: pd.DataFrame, n: int) -> pd.Series:
    by = frame.groupby("secao").agg(k=("cnae_subclasse", "size"), v=("vinculos", "sum"))
    raw = n * (0.5 * by.k / by.k.sum() + 0.5 * by.v / by.v.sum())
    alloc = np.minimum(np.maximum(raw.round(), MIN_PER_SECTION), by.k).astype(int)
    # adjust to exactly n: change the largest sections that still have room
    while alloc.sum() != n:
        step = 1 if alloc.sum() < n else -1
        room = (alloc < by.k) if step > 0 else (alloc > np.minimum(MIN_PER_SECTION, by.k))
        cand = (raw - alloc)[room]
        s = cand.idxmax() if step > 0 else cand.idxmin()
        alloc[s] += step
    return alloc


def draw(frame: pd.DataFrame, alloc: pd.Series, rng: np.random.Generator) -> pd.DataFrame:
    picks = []
    for secao, n_s in alloc.items():
        sec = frame[frame.secao == secao]
        tiers = sec.groupby("faixa_emprego")
        sizes = tiers.size()
        # equal split across tiers present, capped by tier size, remainder to larger tiers
        quota = pd.Series(n_s // len(sizes), index=sizes.index).clip(upper=sizes)
        for t in sizes.sort_values(ascending=False).index:
            if quota.sum() >= n_s:
                break
            quota[t] += min(sizes[t] - quota[t], n_s - quota.sum())
        for t, q in quota.items():
            g = sec[sec.faixa_emprego == t]
            idx = rng.choice(len(g), size=q, replace=False)
            picks.append(g.iloc[idx].assign(prob_inclusao=q / len(g)))
    return pd.concat(picks, ignore_index=True)


def split_dev_test(sample: pd.DataFrame, rng: np.random.Generator) -> pd.Series:
    split = pd.Series("teste", index=sample.index)
    for _, g in sample.groupby("secao"):
        k = round(len(g) * DEV_SHARE)
        split[rng.choice(g.index.to_numpy(), size=k, replace=False)] = "dev"
    return split


def write_sheet(sample: pd.DataFrame, eixos: list[str], path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "anotacao"
    cols = [
        ("cnae_subclasse", 11), ("descricao", 45), ("compreende_nao_compreende", 70),
        ("atividades", 50), ("eixo_principal", 34), ("eixos_secundarios", 34),
        ("nota", 40), ("split", 8),
    ]  # fmt: skip
    head = PatternFill("solid", fgColor="DDEBF7")
    fill = PatternFill("solid", fgColor="FFF2CC")
    for j, (c, w) in enumerate(cols, 1):
        cell = ws.cell(row=1, column=j, value=c)
        cell.font, cell.fill = Font(bold=True), head
        ws.column_dimensions[cell.column_letter].width = w
    # dev rows first: they unblock classifier tuning (ADR-0004)
    order = sample.assign(_o=sample.split != "dev").sort_values(["_o", "cnae_subclasse"])
    for i, r in enumerate(order.itertuples(), 2):
        vals = [r.cnae_subclasse, r.descricao, r.observacoes, (r.atividades or "")[:1500]]
        for j, v in enumerate(vals, 1):
            ws.cell(row=i, column=j, value=v).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=i, column=8, value=r.split)
        for j in (5, 6, 7):
            ws.cell(row=i, column=j).fill = fill
    lists = wb.create_sheet("eixos")
    for i, e in enumerate([*eixos, NAO_SE_APLICA], 1):
        lists.cell(row=i, column=1, value=e)
    last = len(order) + 1
    dv = DataValidation(type="list", formula1=f"=eixos!$A$1:$A${len(eixos) + 1}", allow_blank=True)
    dv.error, dv.errorTitle = "Escolha um eixo da lista", "Eixo inválido"
    ws.add_data_validation(dv)
    dv.add(f"E2:E{last}")
    ws.freeze_panes = "B2"
    instr = wb.create_sheet("instrucoes", 0)
    for i, line in enumerate(
        [
            "Protocolo: annotation/PROTOCOLO.md",
            "1. Leia descrição, 'compreende / não compreende' e atividades da subclasse.",
            ("2. eixo_principal: escolha 1 eixo na lista (ou 'Não se aplica' se nenhum curso "
            "técnico forma para a atividade)."),
            "3. eixos_secundarios: opcional, nomes dos eixos separados por ';'.",
            "4. Dúvidas em 'nota'. Não consulte classificadores nem a planilha do outro avaliador.",
            "Cada avaliador anota a sua cópia, de forma independente.",
            "Ordem: as linhas 'dev' (no topo) primeiro; depois as de 'teste' (ADR-0004).",
        ],
        1,
    ):
        instr.cell(row=i, column=1, value=line)
    instr.column_dimensions["A"].width = 110
    wb.save(path)


def main(n: int = 300) -> None:
    rng = np.random.default_rng(SEED)
    cnae = pd.read_csv(DATA / "external" / "cnae_subclasses.csv", dtype=str)
    emp = employment()
    frame = cnae.assign(vinculos=cnae.cnae_subclasse.map(emp).fillna(0.0))
    terc = frame.vinculos.rank(method="first").pipe(pd.qcut, 3, labels=["baixo", "medio", "alto"])
    frame["faixa_emprego"] = terc.astype(str)
    alloc = allocate(frame, n)
    sample = draw(frame, alloc, rng)
    sample["split"] = split_dev_test(sample, rng)
    for c in ("eixo_principal", "eixos_secundarios", "nao_se_aplica", "nota"):
        sample[c] = ""
    gold = sample[
        ["cnae_subclasse", "descricao", "eixo_principal", "eixos_secundarios", "nao_se_aplica",
         "nota", "split", "secao", "faixa_emprego", "vinculos", "prob_inclusao"]
    ].sort_values("cnae_subclasse")  # fmt: skip
    gold["vinculos"] = gold.vinculos.round(1)
    gold.to_csv(REFERENCE / "gold_v1.csv", index=False)
    eixos = sorted(pd.read_csv(DATA / "external" / "cnct4_cursos.csv").eixo.unique())
    for who in ("A", "B"):
        write_sheet(sample, eixos, ROOT / "annotation" / f"anotacao_avaliador_{who}.xlsx")
    summary = gold.groupby("secao").agg(
        n=("cnae_subclasse", "size"), dev=("split", lambda s: (s == "dev").sum())
    )
    summary["universo"] = frame.groupby("secao").size()
    print(summary.T.to_string())
    print(f"total {len(gold)} | dev {(gold.split == 'dev').sum()} | "
          f"emprego coberto {gold.vinculos.sum() / frame.vinculos.sum():.1%}")  # fmt: skip


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
