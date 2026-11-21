"""Desambiguação por LLM com saída estruturada e cache em disco (spec 02).

Calls OpenRouter's OpenAI-compatible API (key in env `OPENROUTER_API_KEY`, never in the repo).
Subclasses go in batches; the model gets every CNCT axis with its courses, the subclass text and
the top-k course candidates of the text classifier (flagged as possibly wrong), and returns one
JSON object per subclass. Temperature 0; responses cached by hash of (model, prompt).
Per ADR-0004 the model must not be the one that produced the reference annotation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time

import pandas as pd
import requests

from tcc_aderencia.config import ROOT

API = "https://openrouter.ai/api/v1/chat/completions"
CACHE = ROOT / ".cache" / "llm"
NAO_SE_APLICA = "Não se aplica (nenhum curso técnico)"
# Two free models from different providers (spec 02). Gemma (Google) was dropped: persistently
# rate-limited upstream on 2026-11-20. ERNIE was the best single model on the dev split.
DEFAULT_MODELS = ("baidu/ernie-5.5-flash-preview:free", "nvidia/nemotron-3-ultra-550b-a55b:free")
PRIMARY = DEFAULT_MODELS[0]

SYSTEM = f"""Você classifica atividades econômicas (subclasses da CNAE 2.3) nos eixos tecnológicos do \
Catálogo Nacional de Cursos Técnicos (CNCT, 4ª ed.). Para cada subclasse, escolha o eixo do curso \
técnico que forma profissionais para exercer a atividade principal dela. Use "{NAO_SE_APLICA}" somente se \
nenhum curso técnico forma para a atividade. Responda APENAS com um array JSON, um objeto por \
subclasse, no formato: [{{"cnae_subclasse": "...", "eixo": "...", "cursos": ["..."], \
"justificativa": "uma frase"}}]. O campo "eixo" deve ser exatamente um dos nomes da lista."""


def is_ambiguous(top1: float, top2: float, tau: float, delta: float) -> bool:
    """Spec 02 rule: send to the LLM when the best score is low or the margin is small."""
    return top1 < tau or (top1 - top2) < delta


def axes_block(cnct: pd.DataFrame) -> str:
    c = cnct[cnct.eixo != "Militar"]
    lines = [
        f"- {e}: " + "; ".join(g.curso.str.replace("Técnico em ", "", regex=False))
        for e, g in c.groupby("eixo")
    ]
    lines += ["- Militar: cursos das Forças Armadas", f"- {NAO_SE_APLICA}"]
    return "Eixos e cursos:\n" + "\n".join(lines)


def item_block(row: dict, candidates: list[str]) -> str:
    cand = "; ".join(candidates) if candidates else "—"
    return (
        f"cnae_subclasse: {row['cnae_subclasse']}\n"
        f"descrição: {row['descricao']}\n"
        f"compreende: {str(row.get('compreende', ''))[:600]}\n"
        f"sugestões do classificador de texto (podem estar erradas): {cand}"
    )


def _call(model: str, messages: list[dict], retries: int = 12) -> str:
    key = os.environ["OPENROUTER_API_KEY"]
    for attempt in range(retries):
        r = requests.post(
            API,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "messages": messages, "temperature": 0},
            timeout=300,
        )
        if r.status_code == 200:
            body = r.json()
            if body.get("choices"):
                return body["choices"][0]["message"]["content"] or ""
        time.sleep(min(120, 5 * 2**attempt))
    raise RuntimeError(f"{model}: HTTP {r.status_code} {r.text[:200]}")


def _parse(text: str) -> list[dict]:
    m = re.search(r"\[.*\]", text, re.DOTALL)
    return json.loads(m.group(0)) if m else []


def resolve_batch(rows: list[dict], candidates: dict[str, list[str]], model: str, axes: str):
    """Classify a batch; returns list of dicts (cnae_subclasse, eixo, cursos, justificativa)."""
    user = axes + "\n\nSubclasses:\n\n" + "\n\n".join(
        item_block(r, candidates.get(r["cnae_subclasse"], [])) for r in rows
    )
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    key = hashlib.sha256(json.dumps([model, messages], ensure_ascii=False).encode()).hexdigest()
    path = CACHE / f"{key[:20]}.json"
    if path.exists():
        text = json.loads(path.read_text())["text"]
    else:
        text = _call(model, messages)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": model, "text": text}, ensure_ascii=False))
    return _parse(text)


def resolve(cnae_row: dict, candidates: list[dict], model: str) -> dict:
    """Single-subclass convenience wrapper (spec 02 signature)."""
    from tcc_aderencia.config import DATA

    axes = axes_block(pd.read_csv(DATA / "external" / "cnct4_cursos.csv"))
    names = [c["curso"] if isinstance(c, dict) else str(c) for c in candidates]
    out = resolve_batch([cnae_row], {cnae_row["cnae_subclasse"]: names}, model, axes)
    return out[0] if out else {}


def classify(
    cnae: pd.DataFrame,
    candidates: pd.DataFrame,
    model: str,
    cnct: pd.DataFrame,
    batch_size: int = 10,
    top_k: int = 3,
) -> pd.DataFrame:
    """cnae: cnae_subclasse, descricao, compreende. candidates: output of ranking.rank.

    Returns cnae_subclasse, eixo_pred, cursos, justificativa, modelo (invalid axes → NaN).
    """
    valid = set(cnct.eixo) | {NAO_SE_APLICA}
    axes = axes_block(cnct)
    cand = (
        candidates[candidates["rank"] <= top_k]
        .groupby("cnae_subclasse")
        .curso.apply(lambda s: [c.replace("Técnico em ", "") for c in s])
        .to_dict()
    )
    rows = cnae.to_dict("records")
    out = []
    for i in range(0, len(rows), batch_size):
        for r in resolve_batch(rows[i : i + batch_size], cand, model, axes):
            if isinstance(r, dict) and "cnae_subclasse" in r:
                out.append(r)
    df = pd.DataFrame(out, columns=["cnae_subclasse", "eixo", "cursos", "justificativa"])
    df["cnae_subclasse"] = df.cnae_subclasse.astype(str).str.replace(r"\D", "", regex=True)
    df = df.drop_duplicates("cnae_subclasse").rename(columns={"eixo": "eixo_pred"})
    df.loc[~df.eixo_pred.isin(valid), "eixo_pred"] = pd.NA
    return df.assign(modelo=model)


def combine(preds: dict[str, pd.DataFrame], primary: str = PRIMARY) -> pd.DataFrame:
    """Final T axis per subclass, rule fixed on the dev split BEFORE looking at the test split:
    agreement of the two providers → that axis; disagreement → the primary model; one missing
    → the one available. Columns: cnae_subclasse, eixo_pred, consenso (bool), n_modelos."""
    wide = None
    for m, df in preds.items():
        d = df[["cnae_subclasse", "eixo_pred"]].rename(columns={"eixo_pred": m})
        wide = d if wide is None else wide.merge(d, on="cnae_subclasse", how="outer")
    models = list(preds)
    vals = wide[models]
    first = vals[primary].fillna(vals.bfill(axis=1).iloc[:, 0])
    return pd.DataFrame(
        {
            "cnae_subclasse": wide.cnae_subclasse,
            "eixo_pred": first,
            "consenso": vals.nunique(axis=1).eq(1) & vals.notna().all(axis=1),
            "n_modelos": vals.notna().sum(axis=1),
        }
    )


# --- Second pass: multi-course weights (ADR-0005, P20) ----------------------------------------

SYSTEM_COURSES = """Você distribui os empregos de nível técnico de atividades econômicas (subclasses da \
CNAE 2.3) entre os cursos do Catálogo Nacional de Cursos Técnicos (CNCT, 4ª ed.). Para cada subclasse, \
liste TODOS os cursos técnicos, de qualquer eixo, cujos egressos trabalham nas atividades dela \
(produção, manutenção, controle, gestão, segurança, meio ambiente etc.), com um peso entre 0 e 1 \
proporcional à parcela dos empregos técnicos da subclasse ligada a cada curso; os pesos somam 1. \
Use de 1 a 6 cursos; omita cursos com peso < 0,05. O eixo principal já definido para a subclasse vem \
indicado e deve estar representado. Use os nomes dos cursos exatamente como na lista, sem "Técnico em". \
Responda APENAS com um array JSON: [{"cnae_subclasse": "...", "cursos": [{"curso": "...", \
"peso": 0.0}]}]."""


def course_weights(
    cnae: pd.DataFrame,
    final: pd.DataFrame,
    model: str,
    cnct: pd.DataFrame,
    batch_size: int = 10,
) -> pd.DataFrame:
    """w_T(s, c) from the LLM listing every related course with weights.

    cnae: cnae_subclasse, descricao, compreende. final: cnae_subclasse, eixo_pred (the axis
    evaluated in G2; "não se aplica" subclasses are skipped). Returns cnae_subclasse, curso
    (CNCT name), eixo, w_T (renormalized to 1 over valid courses), modelo.
    """
    from tcc_aderencia.ingest.pnp import norm_course

    civil = cnct[cnct.eixo != "Militar"]
    lookup = {norm_course(c): c for c in civil.curso}
    axis_of = dict(zip(civil.curso, civil.eixo, strict=True))
    axes = axes_block(cnct)
    x = cnae.merge(final[["cnae_subclasse", "eixo_pred"]], on="cnae_subclasse")
    x = x[x.eixo_pred.notna() & (x.eixo_pred != NAO_SE_APLICA)]
    rows = x.to_dict("records")
    out = []
    for i in range(0, len(rows), batch_size):
        b = rows[i : i + batch_size]
        user = axes + "\n\nSubclasses:\n\n" + "\n\n".join(
            f"cnae_subclasse: {r['cnae_subclasse']}\ndescrição: {r['descricao']}\n"
            f"compreende: {str(r.get('compreende', ''))[:600]}\neixo principal: {r['eixo_pred']}"
            for r in b
        )
        messages = [{"role": "system", "content": SYSTEM_COURSES}, {"role": "user", "content": user}]
        for item in _cached(model, messages):
            if not isinstance(item, dict):
                continue
            s = re.sub(r"\D", "", str(item.get("cnae_subclasse", "")))
            for c in item.get("cursos") or []:
                if not isinstance(c, dict):
                    continue
                name = lookup.get(norm_course(c.get("curso", "")))
                try:
                    peso = float(c.get("peso", 0))
                except (TypeError, ValueError):
                    peso = 0.0
                if name and peso > 0:
                    out.append((s, name, axis_of[name], peso))
    df = pd.DataFrame(out, columns=["cnae_subclasse", "curso", "eixo", "w_T"])
    df = df.groupby(["cnae_subclasse", "curso", "eixo"], as_index=False).w_T.sum()
    df["w_T"] = df.w_T / df.groupby("cnae_subclasse").w_T.transform("sum")
    return df.assign(modelo=model)


def _cached(model: str, messages: list[dict]) -> list:
    key = hashlib.sha256(json.dumps([model, messages], ensure_ascii=False).encode()).hexdigest()
    path = CACHE / f"{key[:20]}.json"
    if path.exists():
        text = json.loads(path.read_text())["text"]
    else:
        text = _call(model, messages)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": model, "text": text}, ensure_ascii=False))
    return _parse(text)
