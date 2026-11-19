import pytest

from tcc_aderencia.ingest.rais import is_vinculos_file


@pytest.mark.parametrize(
    ("name", "year", "expected"),
    [
        ("/pdet/microdados/RAIS/2012/AC2012.7z", 2012, True),
        ("/pdet/microdados/RAIS/2012/Estb2012.7z", 2012, False),
        ("/pdet/microdados/RAIS/2017/ESTB2017.7z", 2017, False),
        ("/pdet/microdados/RAIS/2017/SP2017.7z", 2017, True),
        ("/pdet/microdados/RAIS/2019/RAIS_VINC_PUB_NORTE.7z", 2019, True),
        ("/pdet/microdados/RAIS/2019/RAIS_ESTAB_PUB.7z", 2019, False),
        ("/pdet/microdados/RAIS/2024/RAIS_VINC_PUB_SP.7z", 2024, True),
        ("/pdet/microdados/RAIS/2024/LEIAME.txt", 2024, False),
    ],
)
def test_is_vinculos_file(name, year, expected):
    assert is_vinculos_file(name, year) is expected
