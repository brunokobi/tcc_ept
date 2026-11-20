import numpy as np
import pandas as pd
import pytest

from tcc_aderencia.index.aderencia import (
    attach_to_offers,
    axis_employment_share,
    cycle_indices,
    linked_employment,
    location_quotient,
    shift_share,
)


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


# --- spec 03 v2: Q, S, B ---------------------------------------------------------------------


@pytest.fixture
def panel():
    # two territories, two subclasses (agro, ti) + one unmapped, years 2018-2020
    rows = []
    for ano, k in [(2018, 1.0), (2019, 1.0), (2020, 1.5)]:
        rows += [
            ("R1", ano, "0111301", 60 * k), ("R1", ano, "6201501", 30.0), ("R1", ano, "9001", 10.0),
            ("R2", ano, "0111301", 10.0), ("R2", ano, "6201501", 90.0 * k), ("R2", ano, "9001", 0.0),
            ("R3", ano, "0111301", 30.0), ("R3", ano, "6201501", 30.0), ("R3", ano, "9001", 40.0),
        ]
    return pd.DataFrame(rows, columns=["territorio", "ano", "cnae_subclasse", "vinculos"])


@pytest.fixture
def w():
    return pd.DataFrame(
        {"cnae_subclasse": ["0111301", "6201501"], "unidade": ["Agro", "TI"], "w": [1.0, 1.0]}
    )


def test_linked_share_bounds_and_national_ql(panel, w):
    lk = linked_employment(panel, w)
    assert ((lk.P >= 0) & (lk.P <= 1)).all()
    assert (lk.groupby(["territorio", "ano"]).P.sum() <= 1 + 1e-12).all()
    # national QL = 1: job-weighted mean of territorial QL (all cells have L > 0 here)
    tot = panel.groupby("ano").vinculos.sum()
    lk["wq"] = lk.total * lk.QL / lk.ano.map(tot)
    assert lk.groupby(["ano", "unidade"]).wq.sum().to_numpy() == pytest.approx(1.0)
    q = lk.set_index(["territorio", "ano", "unidade"]).QL
    assert q[("R1", 2018, "Agro")] > 1  # sentinel: agricultural territory


def test_cycle_indices(panel, w):
    cyc = pd.DataFrame({"territorio": ["R1"], "curso": ["Agro"], "t0": [2019], "t1": [2020]})
    out = cycle_indices(cyc, panel, w, "curso").iloc[0]
    assert out.Q == pytest.approx(np.log(0.6 / (100 / 300)))
    assert out.S == pytest.approx(np.log(90 / 60))
    # leave-one-out growth of agro outside R1 is zero (R2, R3 constant)
    assert out.B == pytest.approx(0.0)


def test_shift_share_leave_one_out(panel, w):
    cells = pd.DataFrame({"territorio": ["R2"], "unidade": ["Agro"], "t0": [2019], "t1": [2020]})
    b = shift_share(panel, w, cells).B.iat[0]
    # outside R2, agro goes 60+30=90 -> 90+30=120
    assert b == pytest.approx(np.log(120 / 90))


def test_missing_cell_gives_nan_q(panel, w):
    cyc = pd.DataFrame({"territorio": ["R1"], "curso": ["Saúde"], "t0": [2019], "t1": [2020]})
    out = cycle_indices(cyc, panel, w, "curso").iloc[0]
    assert np.isnan(out.Q) and out.L == 0
