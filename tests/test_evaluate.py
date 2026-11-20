import numpy as np
import pandas as pd
import pytest

from tcc_aderencia.classifier.evaluate import bootstrap_f1, krippendorff_nominal, per_axis_metrics


def frames(y, p):
    ids = [str(i) for i in range(len(y))]
    return (
        pd.DataFrame({"cnae_subclasse": ids, "eixo_principal": y}),
        pd.DataFrame({"cnae_subclasse": ids, "eixo_pred": p}),
    )


def test_per_axis_metrics_known_values():
    g, p = frames(["A", "A", "B", "B"], ["A", "B", "B", "B"])
    t = per_axis_metrics(g, p).set_index("eixo")
    assert t.loc["A", "precisao"] == pytest.approx(1.0)
    assert t.loc["A", "revocacao"] == pytest.approx(0.5)
    assert t.loc["B", "precisao"] == pytest.approx(2 / 3)
    assert t.loc["micro", "f1"] == pytest.approx(0.75)
    assert t.loc["macro", "f1"] == pytest.approx((2 / 3 + 0.8) / 2)


def test_bootstrap_ci_contains_point():
    rng = np.random.default_rng(0)
    y = rng.choice(list("ABC"), 200)
    p = np.where(rng.random(200) < 0.7, y, rng.choice(list("ABC"), 200))
    f1, lo, hi = bootstrap_f1(*frames(y, p), n=200)
    assert lo <= f1 <= hi


def test_krippendorff_perfect_and_missing():
    perfect = pd.DataFrame({"A": ["x", "y", "z", "x"], "B": ["x", "y", "z", "x"]})
    assert krippendorff_nominal(perfect) == pytest.approx(1.0)
    with_nan = pd.DataFrame({"A": ["x", "y", None, "x"], "B": ["x", "y", "z", "x"]})
    assert krippendorff_nominal(with_nan) == pytest.approx(1.0)
