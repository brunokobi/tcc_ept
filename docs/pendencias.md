# Pendências e pontos a verificar

| ID | Pendência | Por que importa | Onde decide | Status |
|---|---|---|---|---|
| P1 | Localização do aluno/polo na PNP | Território do aluno EaD (H2) | ADR-0002 | **resolvido:** só município da unidade (EaD registrada na unidade, sem polo); ADR-0002 aceita |
| P2 | Edição do CNCT (4ª × 5ª) | Classificador e robustez | ADR-0001 | aberto |
| P3 | CBO por curso no CNCT | Ponte O | spec 02 | **resolvido:** 164/189 cursos civis; ponte O testada |
| P4 | Granularidade da RAIS | Índices | spec 01 | **resolvido:** microdados com município × subclasse × CBO, 1985–2025 |
| P5 | Série da PNP e quebra de 2024 | Harmonização | spec 01 | **parcial:** edições 2018–2023 baixadas (safras 2017–2022); 2018 sem código de ciclo (**reconstruído**, ver o log da spec 01) e com categorias diferentes (harmonizadas); edições 2024–2025 a verificar se existem. No dados.gov.br, a última é a "Eficiência Acadêmica 2023" (arquivo alterado em 14/02/2025); a nota técnica do MEC diz que, a partir da edição 2024, matrícula e eficiência vêm unificadas (quebra de formato) |
| P6 | Fonte de eventos (estudo de evento) | Extensão | spec 04 | rebaixado a extensão; CNPJ |
| P7 | Template do artigo IFSul | `paper/` | orientador | aberto |
| P8 | Escopo do produto técnico | Prazo | orientador | **proposto:** extensão pós-G4 |
| P9 | Revisão sistemática | Lacuna declarada | protocolo | aberto |
| P10 | Volume de ofertas EaD e ciclos por oferta | Poder para H2 e FE | prospecção PNP | **parcial:** 111 ofertas/270 ciclos EaD por safra; 56% em Gestão. **MDE calculado** (relatório de viabilidade, §9): H1a ≈ 0,8 p.p. e H2 ≈ 4,3–5,3 p.p. de evasão por 1 dp de Q. H2 fica com poder limitado e o EP agrupado é anticonservador (tamanho de 8–15%) |
| P11 | Campi com ≥ 2 cursos / cursos em ≥ 2 campi | FE cruzados de H1a | prospecção PNP | **resolvido:** 563/624 campi; 107/140 cursos (99% das matrículas) |
| P12 | Avaliador humano para a amostra de referência | Validade do gabarito | orientador | aberto: ADR-0004 (proposta) — referência anotada por LLM; falta revisão humana de uma subamostra do teste (~60–100) para medir concordância humano × LLM |
| P13 | RAIS 2012–2024 com mapa de colunas por ano (layouts por UF até 2017, regionais 2018–2023, novo 2024+) | Ingestão | spec 01 | **parcial:** 2012 testado (AC, ES), com as mesmas colunas de 2019, já reconhecidas pelo `rais.py`; filtro de arquivos por UF (`AC2012.7z`, sem `ESTB`) implementado. **Resolvido em 19/11/2026:** 2012–2025 agregados; totais nacionais iguais ao oficial, exceto 2019 (P16). Ver `prospeccao/verificacao-dados-completos.md` |
| P14 | Campos deslocados nos JSON da PNP | Ingestão | spec 01 | contornado: usar CSV |
| P15 | Inferência de H2 com poucos territórios EaD (97 RGIs; 5 delas concentram 48% das matrículas EaD) | Validade do teste de H2 | spec 04 / pré-registro | aberto: pré-registrar bootstrap selvagem por cluster ou inferência por randomização para H2 |
| P16 | Total da RAIS 2019 1,76% abaixo do estoque oficial (46,72 contra 47,56 mi); os outros anos batem com diferença < 0,03% | Série da RAIS / critério de aceite da spec 01 | spec 01 | aberto: conferir na tabela do PDET; sensibilidade sem 2019 |
| P17 | ~1% dos vínculos de 2012–2017 com subclasse CNAE 2.0 fora da lista 2.3 | Classificador CNAE → eixo | spec 02 | **resolvido:** são 24 códigos (subclasses divididas ou renumeradas na 2.1–2.3); tabela curada em `data/reference/cnae_correspondencia_23.csv`, repartida pelo emprego de 2018 (`tcc_aderencia.ingest.cnae.harmonize`). Falta conferir contra as tabelas do IBGE, sobretudo o `8630505` |
| P18 | CBOs genéricas no CNCT geram ruído no mapa O: Recursos Humanos inclui `411010` (assistente administrativo) e Gastronomia `513205` (cozinheiro geral), presentes em quase todo setor | Validade do caminho O (validação de T) | spec 02 / ADR | aberto: avaliar ponderar as CBOs pela especificidade setorial (estilo TF-IDF) ou excluir as ubíquas; decisão por ADR antes de comparar T × O |
| P19 | Classificador T. Dev (referência LLM, 99): TF-IDF 0,62 / macro-F1 0,51 [0,42; 0,63]; embeddings e5 0,59 / 0,49; caminho O 0,54 / 0,37; **LLM Nemotron (NVIDIA) 0,87 / 0,83 [0,74; 0,91]; ERNIE (Baidu) 0,90 / 0,86 [0,79; 0,93]**; alfa entre os dois LLMs 0,93. Gemma (Google) descartado por limite de taxa persistente. **Regra fixada no dev antes do teste** (`llm.combine`): consenso dos dois; desacordo → ERNIE | Marco G2 | spec 02 | parcial: G2 atingido no dev (IC sem sobreposição com a baseline); falta a avaliação única no teste (201). Ressalva: referência e classificador são LLMs (ADR-0004) |
