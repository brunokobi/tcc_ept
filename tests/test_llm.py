import pandas as pd

from tcc_aderencia.classifier import llm


def test_is_ambiguous():
    assert llm.is_ambiguous(0.1, 0.05, tau=0.2, delta=0.01)  # low top1
    assert llm.is_ambiguous(0.5, 0.49, tau=0.2, delta=0.05)  # small margin
    assert not llm.is_ambiguous(0.5, 0.3, tau=0.2, delta=0.05)


def test_parse_extracts_json_array_from_chatty_text():
    text = 'Claro!\n```json\n[{"cnae_subclasse": "0111302", "eixo": "Recursos Naturais"}]\n```'
    assert llm._parse(text) == [{"cnae_subclasse": "0111302", "eixo": "Recursos Naturais"}]
    assert llm._parse("sem json") == []


def test_classify_validates_axes(monkeypatch):
    cnct = pd.DataFrame({"curso": ["Técnico em Agricultura"], "eixo": ["Recursos Naturais"]})
    reply = [
        {"cnae_subclasse": "0111-3/02", "eixo": "Recursos Naturais", "cursos": [], "justificativa": ""},
        {"cnae_subclasse": "0112199", "eixo": "Eixo Inventado", "cursos": [], "justificativa": ""},
    ]
    monkeypatch.setattr(llm, "resolve_batch", lambda *a, **k: reply)
    cnae = pd.DataFrame({"cnae_subclasse": ["0111302", "0112199"], "descricao": ["a", "b"]})
    cand = pd.DataFrame({"cnae_subclasse": [], "rank": [], "curso": []})
    out = llm.classify(cnae, cand, "m", cnct).set_index("cnae_subclasse")
    assert out.loc["0111302", "eixo_pred"] == "Recursos Naturais"  # code normalized
    assert pd.isna(out.loc["0112199", "eixo_pred"])  # invalid axis rejected


def test_combine_rule():
    a = pd.DataFrame({"cnae_subclasse": ["1", "2", "3"], "eixo_pred": ["X", "X", None]})
    b = pd.DataFrame({"cnae_subclasse": ["1", "2", "3"], "eixo_pred": ["X", "Y", "Z"]})
    out = llm.combine({"p": a, "q": b}, primary="p").set_index("cnae_subclasse")
    assert out.loc["1", "eixo_pred"] == "X" and out.loc["1", "consenso"]
    assert out.loc["2", "eixo_pred"] == "X" and not out.loc["2", "consenso"]  # primary wins
    assert out.loc["3", "eixo_pred"] == "Z" and out.loc["3", "n_modelos"] == 1  # fallback
