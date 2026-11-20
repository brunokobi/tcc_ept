# Spec 01 — Fontes de dados e harmonização

## Fontes

| Fonte | Conteúdo usado | Granularidade alvo | Módulo | Saída (`data/processed/`) |
|---|---|---|---|---|
| CNPJ (Receita Federal) | estabelecimentos ativos: CNAE principal (e secundárias), porte, município, data de abertura/baixa | estabelecimento → município × CNAE subclasse × ano | `ingest/cnpj.py` (reaproveita pipeline existente via `CNPJ_PIPELINE_PATH`) | `estab_mun_cnae_ano.parquet` |
| RAIS (PDET) | vínculos ativos em 31/12 | município × CNAE subclasse × ano | `ingest/rais.py` | `rais_mun_cnae_ano.parquet` |
| Plataforma Nilo Peçanha | cursos, modalidade, tipo, vagas, matrículas, ciclos, evasão, conclusão, eficiência | curso × campus × ciclo | `ingest/pnp.py` | `pnp_ciclos.parquet` |
| CNCT | eixos, cursos, perfil profissional, campo de atuação, (CBO?) | curso | `ingest/cnct.py` | `cnct_cursos.parquet` |
| IBGE (divisão regional 2017) | município → região imediata → intermediária; código IBGE | município | `ingest/ibge.py` | `territorios.parquet` |
| CNAE 2.x (IBGE/CONCLA) | descrição e notas explicativas das subclasses | subclasse | `ingest/cnct.py` ou `ingest/cnae.py` | `cnae_subclasses.parquet` |

## Chaves de junção
- **Município:** código IBGE 7 dígitos em todas as tabelas (CNPJ usa código TOM/Receita → tabela de conversão obrigatória).
- **CNAE:** subclasse 7 dígitos, sem pontuação.
- **Curso:** nome do curso PNP normalizado → curso CNCT (matching por nome + eixo; resolver exceções em `data/reference/pnp_cnct_overrides.csv`).
- **Território:** `cod_rgi` (região geográfica imediata) por padrão; ver ADR-0002.

## Harmonização
- Série histórica da PNP: documentar anos, mudanças de definição de indicador e regras aplicadas em `docs/spec/01-fontes-de-dados.md#log` (abaixo).
- CNPJ é um snapshot: reconstruir estoque por ano usando data de início de atividade e data de situação cadastral (baixa).
- Formatos: Parquet; leitura/joins pesados com DuckDB.
- Cada script de ingestão é idempotente e registra fonte, URL, data de download e hash em `data/raw/<fonte>/MANIFEST.json`.

## Critérios de aceite
- [ ] 100% dos municípios da PNP mapeados para território IBGE.
- [ ] ≥ 95% das ofertas PNP associadas a curso CNCT (resto listado).
- [ ] Totais de vínculos RAIS por UF batem com o publicado no PDET (±1%).

## Log de harmonização
- **PNP: unidade de observação.** Cada linha dos microdados de eficiência é uma matrícula, em todas as edições. Na edição 2018, o campo "Número de registros" não é peso.
- **PNP 2018: ciclo reconstruído.** A edição não tem `Código do Ciclo Matricula`. O ciclo é reconstruído por unidade + curso + data de início + data de fim previsto + modalidade + tipo de oferta (`ingest.pnp.CYCLE_KEY`). Validação em 2019 e 2023, onde o código existe: a chave nunca divide um ciclo real e junta dois ciclos na mesma chave em 0,3% (2019) e 0,9% (2023) das chaves. O turno foi excluído, porque divide ciclos reais. Resultado: 3.925 ciclos e 193.343 matrículas, coluna `ciclo_reconstruido`.
- **PNP: categorias de situação.** Evasão = `Evadidos` (2019+) ou `Evasão` (2018); conclusão = `Concluintes`/`Concluídos` (2023 separa os dois) ou `Conclusão` (2018).
- **PNP ↔ CNCT:** nome normalizado (sem acento e sem "técnico em"), depois nomenclaturas anteriores do CNCT, depois exceções em `data/reference/pnp_cnct_overrides.csv` (7 nomes). Cobertura: 99,99% das matrículas de 2018–2023; fica de fora só Infantaria (militar). O eixo registrado na PNP diverge do eixo do CNCT em 0,8% dos ciclos (por exemplo, Biotecnologia aparece em Ambiente e Saúde na PNP e em Produção Industrial no CNCT); **usa-se o eixo do CNCT**.
- **RAIS: CNAE.** 24 subclasses antigas (2.0–2.2) são convertidas para a 2.3 por `ingest.cnae.harmonize` (P17).
- **RAIS: CBO.** O layout 2023+ grava o CBO sem o zero à esquerda; a ingestão completa o código até 6 dígitos.
- Saída: `data/processed/pnp_ciclos.parquet` (22.318 ciclos técnicos de 2018–2023).
