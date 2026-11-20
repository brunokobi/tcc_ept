import pandas as pd

from tcc_aderencia.ingest.pnp import match_courses_to_cnct, norm_course

CNCT = pd.DataFrame(
    {
        "curso": ["Técnico em Informática", "Técnico em Análises Clínicas"],
        "eixo": ["Informação e Comunicação", "Ambiente e Saúde"],
        "nomenclaturas_anteriores": [None, "• Patologia clínica\n• Biodiagnóstico"],
    }
)


def test_norm_course():
    assert norm_course("Técnico em  Informática") == "informatica"
    assert norm_course("TÉCNICO EM AUTOMAÇÃO-INDUSTRIAL") == "automacao industrial"


def test_match_current_and_former_names():
    pnp = pd.DataFrame({"curso": ["técnico em informática", "técnico em biodiagnóstico", "x"]})
    out = match_courses_to_cnct(pnp, CNCT)
    assert out.curso_cnct.tolist()[:2] == ["Técnico em Informática", "Técnico em Análises Clínicas"]
    assert out.eixo_cnct.iat[1] == "Ambiente e Saúde"
    assert pd.isna(out.curso_cnct.iat[2])
