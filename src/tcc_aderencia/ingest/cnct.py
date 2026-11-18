"""Catálogo Nacional de Cursos Técnicos (spec 01/02).

Parses the consolidated CNCT 4th edition PDF (text extracted page by page) into one
row per course with axis, profile, field of work, associated CBO codes and whether the
course may be offered as distance education (EaD).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

COURSE_HEADER = re.compile(r"^(T[ÉE]CNICO EM .+?)\s{1,}(\d{3,4}) horas\s*$")
FOOTER = re.compile(r"CAT[ÁA]LOGO NACIONAL DE CURSOS T[ÉE]CNICOS P[áa]gina \d+ de \d+ (Eixo .+)$")
CBO_CODE = re.compile(r"\b(\d{4})-(\d{2})\b")
CBO_FAMILY = re.compile(r"^\s*(\d{4})\s+-\s", re.M)  # 4-digit CBO family, matched by prefix
SECTIONS = [
    "Perfil Profissional de Conclusão",
    "Carga Horária Mínima",
    "Pré-requisitos para ingresso",
    "Legislação Profissional",
    "Itinerários formativos",
    "Campo de Atuação",
    "Ocupações CBO Associadas",
    "Infraestrutura Mínima",
    "Nomeclaturas anteriores",
]


def extract_pdf_text(pdf_path: Path) -> list[str]:
    import pypdf

    return [p.extract_text() or "" for p in pypdf.PdfReader(str(pdf_path)).pages]


def _split_sections(body: str) -> dict[str, str]:
    pattern = "|".join(re.escape(s) for s in SECTIONS)
    parts = re.split(f"^({pattern})\\s*$", body, flags=re.M)
    out: dict[str, str] = {}
    for name, text in zip(parts[1::2], parts[2::2]):
        out[name] = (out.get(name, "") + "\n" + text).strip()
    return out


def _ead_status(text: str) -> str:
    t = text.lower()
    if "não poderá ser realizado na modalidade ead" in t:
        return "vedado"
    if "poderá ser realizado na modalidade ead" in t:
        return "permitido"
    return "nao_informado"


def parse_cnct_pages(pages: list[str]) -> pd.DataFrame:
    """Group page texts by course header and parse each course block."""
    courses: dict[str, dict] = {}
    order: list[str] = []
    for page in pages:
        lines = [ln.rstrip() for ln in page.splitlines()]
        # course headers may wrap onto a second line ("TÉCNICO EM X EM" / "Y  1200 horas")
        if len(lines) > 1 and re.match(r"^T[ÉE]CNICO EM ", lines[0]) and not lines[0].strip().endswith("horas"):
            lines = [lines[0].strip() + " " + lines[1].strip()] + lines[2:]
        header = next((COURSE_HEADER.match(ln.strip()) for ln in lines[:3] if COURSE_HEADER.match(ln.strip())), None)
        footer = next((FOOTER.search(ln.strip()) for ln in lines[-3:] if FOOTER.search(ln.strip())), None)
        if not header:
            continue
        name = re.sub(r"\s+", " ", header.group(1)).strip()
        body = "\n".join(
            ln for ln in lines if not COURSE_HEADER.match(ln.strip()) and not FOOTER.search(ln.strip())
        )
        if name not in courses:
            courses[name] = {"curso": name, "carga_horaria": int(header.group(2)), "eixo": None, "body": ""}
            order.append(name)
        courses[name]["body"] += "\n" + body
        if footer and not courses[name]["eixo"]:
            courses[name]["eixo"] = footer.group(1).replace("Eixo de ", "").replace("Eixo ", "").strip()

    rows = []
    for name in order:
        c = courses[name]
        sec = _split_sections(c["body"])
        cbo_text = sec.get("Ocupações CBO Associadas", "")
        cbo = sorted({a + b for a, b in CBO_CODE.findall(cbo_text)} | set(CBO_FAMILY.findall(cbo_text)))
        rows.append(
            {
                "curso": name.title().replace(" Em ", " em ").replace(" De ", " de ").replace(" E ", " e "),
                "eixo": c["eixo"],
                "carga_horaria": c["carga_horaria"],
                "ead": _ead_status(sec.get("Carga Horária Mínima", "")),
                "perfil": sec.get("Perfil Profissional de Conclusão", ""),
                "campo_atuacao": sec.get("Campo de Atuação", ""),
                "cbo_codes": ";".join(cbo),
                "n_cbo": len(cbo),
                "nomenclaturas_anteriores": sec.get("Nomeclaturas anteriores", "").strip("- \n"),
            }
        )
    return pd.DataFrame(rows)


def load_cnct(pdf_path: Path, edition: int = 4) -> pd.DataFrame:
    df = parse_cnct_pages(extract_pdf_text(pdf_path))
    df["cnct_edicao"] = edition
    return df


def load_cnae_subclasses() -> pd.DataFrame:
    """CNAE 2.3 subclasses from the IBGE API (spec 02)."""
    import json
    import urllib.request

    url = "https://servicodados.ibge.gov.br/api/v2/cnae/subclasses"
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.load(r)
    return pd.DataFrame(
        {
            "cnae_subclasse": d["id"],
            "descricao": d["descricao"],
            "classe": d["classe"]["id"],
            "secao": d["classe"]["grupo"]["divisao"]["secao"]["id"],
            "observacoes": " | ".join(d.get("observacoes") or []),
            "atividades": " | ".join(d.get("atividades") or []),
        }
        for d in data
    )
