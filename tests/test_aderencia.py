import pandas as pd
import pytest

from tcc_aderencia.index.aderencia import attach_to_offers, axis_employment_share, location_quotient


@pytest.fixture
def employment():
    return pd.DataFrame(
        {
            "territorio": ["R1", "R1", "R1", "R2", "R2"],
            "cnae_subclasse": ["0111301", "6201501", "9999999", "0111301", "6201501"],
            "ano": [2022] * 5,
            "vinculos": [60, 30, 10, 10, 90],
        }
    )


@pytest.fixture
def mapping():
    return pd.DataFrame(
        {
            "cnae_subclasse": ["0111301", "6201501"],
            "eixo": ["Recursos Naturais", "Informação e Comunicação"],
            "peso": [1.0, 1.0],
        }
    )


def test_share_uses_all_jobs_in_denominator(employment, mapping):
    s = axis_employment_share(employment, mapping).set_index(["territorio", "eixo"])["aderencia"]
    assert s[("R1", "Recursos Naturais")] == pytest.approx(0.6)
    assert s[("R1", "Informação e Comunicação")] == pytest.approx(0.3)
    assert s[("R2", "Informação e Comunicação")] == pytest.approx(0.9)


def test_share_bounded(employment, mapping):
    s = axis_employment_share(employment, mapping)["aderencia"]
    assert ((s >= 0) & (s <= 1)).all()


def test_location_quotient(employment, mapping):
    shares = axis_employment_share(employment, mapping)
    lq = location_quotient(shares, employment, mapping).set_index(["territorio", "eixo"])["ql"]
    # national share of Recursos Naturais = 70/200 = 0.35; R1 = 0.6
    assert lq[("R1", "Recursos Naturais")] == pytest.approx(0.6 / 0.35)


def test_attach_missing_axis_is_zero(employment, mapping):
    shares = axis_employment_share(employment, mapping)
    offers = pd.DataFrame(
        {"oferta_id": [1], "territorio": ["R2"], "ano": [2022], "eixo": ["Saúde"]}
    )
    assert attach_to_offers(offers, shares)["aderencia"].iloc[0] == 0.0
