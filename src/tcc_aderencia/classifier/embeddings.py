"""Similaridade por embeddings sentence-transformers (spec 02)."""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from tcc_aderencia.classifier.ranking import rank
from tcc_aderencia.classifier.texts import cnae_texts, course_texts
from tcc_aderencia.config import ROOT

DEFAULT_MODEL = "intfloat/multilingual-e5-base"
CACHE = ROOT / ".cache" / "embeddings"


def embed(texts: list[str], model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """L2-normalized embeddings, cached on disk by model + text hash."""
    key = hashlib.sha256((model_name + "\x00" + "\x00".join(texts)).encode()).hexdigest()[:16]
    path = CACHE / f"{key}.npy"
    if path.exists():
        return np.load(path)
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name, device="cpu")
    # e5 models expect a task prefix; "query: " on both sides for symmetric similarity
    prefix = "query: " if "e5" in model_name else ""
    vec = model.encode(
        [prefix + t for t in texts], batch_size=16, normalize_embeddings=True, show_progress_bar=False
    )
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(path, vec)
    return vec


def rank_candidates(
    cnae: pd.DataFrame | None = None,
    cnct: pd.DataFrame | None = None,
    top_k: int = 5,
    model_name: str = DEFAULT_MODEL,
):
    """(candidates, axes) — see `ranking.rank`."""
    ct, cc = cnae_texts(cnae), course_texts(cnct)
    sim = embed(ct.texto.tolist(), model_name) @ embed(cc.texto.tolist(), model_name).T
    return rank(sim, ct, cc, top_k)
