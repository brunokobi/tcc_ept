"""Linha de base TF-IDF (spec 02): cosseno entre texto da CNAE e texto do curso."""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from tcc_aderencia.classifier.ranking import rank
from tcc_aderencia.classifier.texts import cnae_texts, course_texts

STOPWORDS = ["a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas", "para", "por", "com", "sem", "que", "ou", "um", "uma", "uns", "umas", "ao", "aos", "se", "sua", "seu", "suas", "seus", "como", "mais", "entre", "sobre", "sob", "este", "esta", "estes", "estas", "isso", "exceto", "inclusive", "outros", "outras", "outro", "outra", "nao", "especificados", "especificadas", "anteriormente", "atividades", "atividade", "servicos", "servico", "tecnico", "tecnica", "curso", "campo", "atuacao", "subclasse", "compreende"]


def similarity(cnae: pd.DataFrame, courses: pd.DataFrame):
    vec = TfidfVectorizer(
        strip_accents="unicode",
        lowercase=True,
        stop_words=STOPWORDS,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    vec.fit(pd.concat([cnae.texto, courses.texto]))
    return cosine_similarity(vec.transform(cnae.texto), vec.transform(courses.texto))


def classify(cnae: pd.DataFrame | None = None, cnct: pd.DataFrame | None = None, top_k: int = 5):
    """(candidates, axes) — see `ranking.rank`."""
    ct, cc = cnae_texts(cnae), course_texts(cnct)
    return rank(similarity(ct, cc), ct, cc, top_k)
