import pandas as pd
import pytest

from tcc_aderencia.ingest.cnae import harmonize

CORR = pd.DataFrame(
    {
        "cnae_origem": ["6201500", "6201500", "4713001"],
        "cnae_23": ["6201501", "6201502", "4713004"],
        "peso": [0.75, 0.25, 1.0],
        "regra": ["x"] * 3,
    }
)


def test_harmonize_splits_and_preserves_total():
    df = pd.DataFrame(
        {
            "mun6": ["1", "1", "1", "1"],
            "cnae_subclasse": ["6201500", "4713001", "0111301", "9999999"],
            "vinculos": [100.0, 10.0, 5.0, 3.0],
        }
    )
    out = harmonize(df, CORR).groupby("cnae_subclasse").vinculos.sum()
    assert out["6201501"] == pytest.approx(75)
    assert out["6201502"] == pytest.approx(25)
    assert out["4713004"] == pytest.approx(10)
    assert out["0111301"] == pytest.approx(5)
    assert "9999999" not in out.index  # "ignorado" dropped
    assert out.sum() == pytest.approx(115)
