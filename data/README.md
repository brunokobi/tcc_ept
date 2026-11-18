# Dados

| Pasta | Conteúdo | No git? | Como reproduzir |
|---|---|---|---|
| `pnp/` | Microdados de **eficiência acadêmica** da Plataforma Nilo Peçanha, edições 2018–2023 (safras de ciclos encerrados em 2017–2022), convertidos de CSV para Parquet (zstd), todas as colunas como texto | ✅ | Baixar os CSVs em https://dadosabertos.mec.gov.br/pnp e converter (ver abaixo) |
| `external/cnct4_cursos.csv` | CNCT 4ª ed. (alterada em 29/11/2024), uma linha por curso: eixo, perfil, campo de atuação, CBO, permissão de EaD | ✅ | `tcc_aderencia.ingest.cnct.load_cnct(pdf)` |
| `external/cnae_subclasses.csv` | CNAE 2.3, 1.332 subclasses com atividades e notas | ✅ | `tcc_aderencia.ingest.cnct.load_cnae_subclasses()` |
| `external/ibge_municipios_rgi.csv` | Municípios × regiões imediatas e intermediárias (IBGE 2017) | ✅ | API de localidades do IBGE |
| `reference/` | Amostra de referência anotada (CNAE → eixo) | ✅ | Anotação manual (`annotation/PROTOCOLO.md`) |
| `raw/`, `interim/` | RAIS (arquivos `.7z` e agregados) | ❌ | `python -m tcc_aderencia.ingest.rais <ano>` |

## PNP: linhas por edição

| Edição | Safra | Linhas | Parquet |
|---|---|---|---|
| 2018 | 2017 | 374.037 | 4,7 MB |
| 2019 | 2018 | 338.848 | 1,9 MB |
| 2020 | 2019 | 383.153 | 8,7 MB |
| 2021 | 2020 | 889.855 | 12,8 MB |
| 2022 | 2021 | 769.717 | 10,0 MB |
| 2023 | 2022 | 801.029 | 4,4 MB |

Conversão usada:

```python
import duckdb
duckdb.sql("""copy (select * from read_csv('microdados_eficiencia_academica_2023.csv', sep=';', header=true, all_varchar=true))
              to 'eficiencia_academica_2023.parquet' (format parquet, compression zstd, compression_level 19)""")
```

Leitura: `duckdb.sql("select * from 'data/pnp/*.parquet'")` ou `pandas.read_parquet(...)`.

## Fontes e licenças
- **PNP** (MEC/SETEC): microdados anonimizados na origem, licença ODbL. Dados redistribuídos sem alteração de conteúdo, só de formato.
- **CNCT** (MEC), **CNAE** e **divisão regional** (IBGE): dados públicos oficiais.
- **RAIS** (MTE/PDET): microdados públicos de vínculos, sem identificação.
