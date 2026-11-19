import numpy as np
import pandas as pd
import pytest

from tcc_aderencia.models.power import minimum_detectable_effect, power_curve, simulate


def test_mde_matches_normal_approximation():
    # b ~ N(0, SE) with constant SE: MDE = (z_.975 + z_.8) * SE = 2.8016 * SE
    rng = np.random.default_rng(0)
    sims = pd.DataFrame({"b_q_ead": rng.normal(0, 0.01, 20000), "se_q_ead": np.full(20000, 0.01)})
    assert minimum_detectable_effect(sims) == pytest.approx(0.028016, rel=0.02)


def test_power_curve_monotone_from_alpha():
    rng = np.random.default_rng(0)
    sims = pd.DataFrame({"b_q": rng.normal(0, 0.01, 2000), "se_q": np.full(2000, 0.01)})
    pw = power_curve(sims, "q", np.array([0.0, 0.01, 0.03]))
    assert pw[0] == pytest.approx(0.05, abs=0.02)
    assert np.all(np.diff(pw) > 0)


def test_simulate_runs_on_small_panel():
    rng = np.random.default_rng(1)
    n = 400
    panel = pd.DataFrame(
        {
            "edicao": rng.choice([2019, 2020], n),
            "campus": rng.choice(list("abcdefgh"), n),
            "curso": rng.choice(list("pqrstu"), n),
            "ead": rng.random(n) < 0.3,
            "matriculas": rng.integers(10, 50, n),
            "evasao": rng.random(n),
        }
    )
    panel["territorio"] = panel["campus"].map(dict(zip("abcdefgh", "xxyyzzww", strict=True)))
    sims = simulate(panel, n_sims=5)
    assert len(sims) == 5
    assert (sims[["se_q", "se_q_ead"]] > 0).all().all()
