"""RAIS public microdata (vínculos) → active jobs by município × CNAE subclass × CBO × year (spec 01).

Downloads each yearly file from the MTE FTP, extracts one archive at a time, aggregates with
DuckDB and deletes the extracted text, so disk use stays at one archive at a time.

Usage: python -m tcc_aderencia.ingest.rais 2019 [2020 ...]
"""

from __future__ import annotations

import ftplib
import json
import sys
import time
from pathlib import Path

import duckdb

from tcc_aderencia.config import INTERIM, RAW

FTP_HOST = "ftp.mtps.gov.br"
FTP_DIR = "/pdet/microdados/RAIS/{year}/"

# Column name candidates across layouts (≤2017 per UF, 2018–2023 regional, 2024+ renamed)
COLS = {
    "mun": ["Município - Código", "Município"],
    "cnae": ["CNAE 2.0 Subclasse - Codigo", "CNAE 2.0 Subclasse"],
    "cbo": ["CBO 2002 Ocupação - Código", "CBO Ocupação 2002"],
    "ativo": ["Ind Vínculo Ativo 31/12 - Código", "Vínculo Ativo 31/12"],
}


def is_vinculos_file(name: str, year: int) -> bool:
    """Vínculos archives: regional `RAIS_VINC_PUB_*` from 2018; one per UF (`AC2017.7z`) before,
    alongside an establishments file (`ESTB2017.7z` / `Estb2012.7z`) that must be skipped."""
    n = Path(name).name.upper()
    if not n.endswith(".7Z"):
        return False
    if year >= 2018:
        return "VINC" in n
    return not n.startswith("ESTB")


def list_vinculos_files(year: int) -> list[str]:
    with ftplib.FTP(FTP_HOST, timeout=120) as ftp:
        ftp.login()
        ftp.encoding = "latin-1"
        names = ftp.nlst(FTP_DIR.format(year=year))
    return sorted(n for n in names if is_vinculos_file(n, year))


def download(remote: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    tmp = dest.with_suffix(".part")
    with ftplib.FTP(FTP_HOST, timeout=600) as ftp, open(tmp, "wb") as fh:
        ftp.login()
        ftp.encoding = "latin-1"
        ftp.retrbinary(f"RETR {remote}", fh.write, blocksize=1 << 20)
    tmp.rename(dest)
    return dest


def _detect(con: duckdb.DuckDBPyConnection, path: Path) -> tuple[str, dict[str, str]]:
    first = path.open("rb").readline().decode("latin-1")
    sep = ";" if first.count(";") > first.count(",") else ","
    names = [
        c[0]
        for c in con.execute(
            f"select * from read_csv('{path}', sep='{sep}', header=true, all_varchar=true, encoding='latin-1') limit 0"
        ).description
    ]
    found = {}
    for key, cands in COLS.items():
        hit = next((c for c in cands if c in names), None)
        if hit is None:
            raise KeyError(f"{path.name}: column for {key!r} not found among {names[:15]}...")
        found[key] = hit
    return sep, found


def aggregate_file(path: Path, year: int, out: Path) -> dict:
    con = duckdb.connect()
    sep, c = _detect(con, path)
    con.execute(f"""
        copy (
          select {year} as ano,
                 substr(trim("{c["mun"]}"), 1, 6) as mun6,
                 lpad(trim("{c["cnae"]}"), 7, '0') as cnae_subclasse,
                 lpad(trim("{c["cbo"]}"), 6, '0') as cbo,
                 count(*) as vinculos
          from read_csv('{path}', sep='{sep}', quote='"', header=true, all_varchar=true, encoding='latin-1')
          where trim("{c["ativo"]}") = '1'
          group by all
        ) to '{out}' (format parquet)
    """)
    n, v = con.execute(f"select count(*), sum(vinculos) from read_parquet('{out}')").fetchone()
    return {"file": path.name, "sep": sep, "cols": c, "cells": n, "vinculos": int(v or 0)}


def ingest_year(year: int, keep_archives: bool = True) -> None:
    import py7zr

    raw_dir = RAW / "rais" / str(year)
    out_dir = INTERIM / "rais" / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for remote in list_vinculos_files(year):
        name = Path(remote).name
        out = out_dir / (Path(name).stem + ".parquet")
        if out.exists():
            print(f"[{year}] {name}: já agregado", flush=True)
            continue
        t0 = time.time()
        archive = download(remote, raw_dir / name)
        ext_dir = raw_dir / "ext"
        with py7zr.SevenZipFile(archive) as z:
            z.extractall(ext_dir)
        for i, txt in enumerate(sorted(ext_dir.iterdir())):
            part = out if i == 0 else out_dir / f"{Path(name).stem}_{i}.parquet"
            info = aggregate_file(txt, year, part)
            info.update(
                remote=remote, archive_bytes=archive.stat().st_size, seconds=round(time.time() - t0)
            )
            manifest.append(info)
            print(
                f"[{year}] {name}: {info['vinculos']:,} vínculos, {info['cells']:,} células, {info['seconds']}s",
                flush=True,
            )
            txt.unlink()
        ext_dir.rmdir()
        if not keep_archives:
            archive.unlink()
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    for y in sys.argv[1:]:
        ingest_year(int(y))
