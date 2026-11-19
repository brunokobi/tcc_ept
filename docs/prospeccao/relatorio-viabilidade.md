# Prospecção inicial dos dados — relatório de viabilidade

Data: 18/11/2026. Objetivo: verificar, com dados reais, se o plano das specs é executável antes de investir no pipeline completo.

## Resumo

> **Atualização de 19/11/2026:** verificação com todos os dados (RAIS 2012–2025 nacional) em [verificacao-dados-completos.md](verificacao-dados-completos.md). Veredito: **projeto viável**; H2 com poder limitado.

| Fonte | Status | Veredito |
|---|---|---|
| CNCT 4ª ed. | baixado e processado | **viável** |
| CNAE 2.3 | baixado (API IBGE) | **viável** |
| IBGE (RGI/RGInt) | baixado | **viável** |
| RAIS vínculos | amostra Norte 2019 e 2024 processada | **viável** |
| Ponte CBO (caminho O) | testada na amostra | **viável como validação, não como mapa principal** |
| Variação temporal da aderência | medida na amostra | **muda o desenho de H1a** |
| PNP microdados (eficiência 2023, matrículas 2023) | processado | **viável; H2 com poder limitado** |
| RAIS 2012–2017 (layout por UF) | AC e ES 2012 testados | **viável** |
| Poder estatístico (MDE) | simulado com a estrutura real (§9) | **H1a com folga; H2 no limite** |

## 1. CNCT (4ª edição, conteúdo alterado em 29/11/2024)
- Fonte: PDF consolidado de 548 páginas (cópia pública em saude.sp.gov.br); parser em `src/tcc_aderencia/ingest/cnct.py` → `data/external/cnct4_cursos.csv`.
- 212 de 214 cursos extraídos (faltam 2 de formatação atípica: Operação de Radar [militar] e Produção de Materiais Didáticos Bilíngues em Libras); 13 eixos; 189 civis (23 do eixo Militar, fora do escopo da Rede Federal).
- **CBO por curso:** 164 dos 189 civis têm ocupações CBO associadas (média ≈ 2,4). Sem CBO: 25, incluindo cursos grandes na Rede (Administração, Agronegócio, Secretariado, Arquivo).
- **EaD por curso:** 188 permitem EaD (mínimo de presencialidade varia), 1 é vedado (Agente Comunitário de Saúde, Lei 11.350/2006), 23 sem informação (majoritariamente militares). Útil como variável de contexto para H2.
- Pendências: 5ª edição (consulta pública) — ver ADR-0001.

## 2. CNAE 2.3
- API `servicodados.ibge.gov.br/api/v2/cnae/subclasses`: **1.332 subclasses, 21 seções**, todas com lista de atividades e notas "compreende / não compreende" (≈ 1.250 caracteres por subclasse) → texto rico para embeddings e LLM.

## 3. IBGE
- `data/external/ibge_municipios_rgi.csv`: 5.571 municípios, **510 regiões imediatas**, 133 intermediárias. Os 6 primeiros dígitos casam 100% com o município da RAIS (testado no Norte).

## 4. RAIS (microdados públicos de vínculos, FTP do MTE)
- Anos disponíveis até **2025** (publicado em 13/05/2026). 2015–2017 por UF; a partir de 2018, 7 arquivos regionais.
- Volume 2015–2024: ≈ 28 GB compactados, ≈ 200 GB descompactados; processamento arquivo a arquivo com DuckDB ≈ 90 s/GB, ≈ 0,5 GB de RAM → **4–5 h no total**; resultado agregado de poucas centenas de MB.
- Colunas necessárias presentes em todos os anos testados: subclasse CNAE 2.0 (7 dígitos, 0% ausente no Norte 2024), município (6 dígitos), vínculo ativo em 31/12, CBO 2002 (≈ 1% fora do padrão).
- **Layout muda entre anos:** 2019 usa `;` e nomes curtos (`CNAE 2.0 Subclasse`, `Município`, `Vínculo Ativo 31/12`, `CBO Ocupação 2002`); 2024 usa `,` e nomes com sufixo ` - Código`. A ingestão precisa de um mapa de colunas por ano (MTE publica de-para desde 2024).
- **2012 (layout por UF), testado em 18/11/2026:** AC e ES têm as mesmas 4 colunas, com os mesmos nomes de 2019 (`Município`, `CNAE 2.0 Subclasse`, `CBO Ocupação 2002`, `Vínculo Ativo 31/12`), separador `;`, 0% de CNAE ou CBO com tamanho errado e número de municípios correto (22 e 78). Cada ano tem 27 arquivos de UF mais um de estabelecimentos (`ESTB`/`Estb`), que o filtro descarta. O volume de 2012–2025 é de ≈ 38 GB compactados.
- Norte 2024: 3,55 milhões de vínculos ativos, 450 municípios, 40.229 células município × subclasse.

## 5. Ponte CBO (caminho O) — teste na amostra Norte 2024
- 90% das CBOs dos cursos aparecem na RAIS; 158 dos 164 cursos com CBO têm vínculos associados.
- 20,5% dos vínculos estão em ocupações de algum curso técnico.
- **Validade de face mista:**
  - Boa: Enfermagem → diálise, SAMU, pronto-socorro; Informática → desenvolvimento e licenciamento de software.
  - Ruim: Agropecuária → "Defesa" e "Regulação das atividades econômicas" (o técnico agrícola formal trabalha muito no setor público; o trabalho no campo é informal ou em outras CBOs).
- **Decisão:** o caminho T (texto com IA) é o mapa principal, porque reflete a noção legal de *arranjo produtivo* (setor); o caminho O é validação de convergência e robustez (R2). A demanda ocupacional direta (vínculos nas CBOs do curso) pode entrar como medida complementar.

## 6. Variação temporal da aderência (crítico para a identificação)
Teste com o mapa O, regiões imediatas do Norte, 2019 × 2024 (`log QL` por RGI × curso):

| Recorte | Pares | Correlação 2019×2024 | Fração da variância intra (5 anos) | Mediana \|Δ log QL\| |
|---|---|---|---|---|
| Todas as células | 9.720 | 0,86 | 7,0% | 0,18 |
| Células com > 50 vínculos ligados | 1.104 | 0,93 | 3,5% | 0,10 |

Choque de demanda `S` = Δ log do emprego ligado ao curso em 5 anos (células > 50): média 0,30, **dp 0,26**, p10–p90 de 0,02 a 0,57.

**Consequência:** com efeito fixo de oferta, H1a seria identificada por ~4% da variância, muito ruído. O desenho foi revisto (spec 04 e pré-projeto v2):
- **H1a/H2:** variação transversal com efeitos fixos de campus × ciclo e curso × ciclo.
- **H1b:** variação intra-oferta do choque `S`, instrumentado por shift-share.

## 7. Plataforma Nilo Peçanha (eficiência acadêmica 2023)
Arquivos baixados manualmente pelo pesquisador em `dados/` (fora do git): `microdados_eficiencia_academica_2023.csv` (400 MB, UTF-8, `;`, decimal `,`) e as versões JSON de eficiência e matrículas 2023.

**Estrutura:** 801.029 matrículas de 13.827 ciclos, 650 unidades, 56 instituições. O arquivo de eficiência de um ano reúne os ciclos com **término previsto no ano anterior** (aqui, 2022): cada edição é uma "safra" de conclusão. O painel de ciclos exige baixar as edições de vários anos.

**Localização (P1):** só há o município da **unidade de ensino** (`Código do Município com DV`). Não há residência do estudante nem polo; as ofertas EaD aparecem registradas na unidade (70 unidades, 70 municípios). → ADR-0002 aceita: território da EaD = território da unidade.

**Cursos técnicos (safra 2022):**

| Modalidade | Ciclos | Ofertas | Matrículas | Evasão | Conclusão | Retidos |
|---|---|---|---|---|---|---|
| Presencial | 3.244 | 2.641 | 131.989 | 40,4% | 48,1% | 11,4% |
| EaD | 270 | 111 | 13.842 | 50,0% | 36,4% | 13,6% |

| Tipo de oferta × modalidade | Matrículas | Evasão |
|---|---|---|
| Integrado, presencial | 80.647 | 28,6% |
| Subsequente, presencial | 35.649 | 58,3% |
| Subsequente, EaD | 13.292 | 49,3% |
| Concomitante, presencial | 9.276 | 57,5% |
| PROEJA integrado, presencial | 5.913 | 65,2% |

- A evasão do subsequente (adultos) é o dobro da do integrado, o que é coerente com o mecanismo de custo de oportunidade (H1b), que deve aparecer mais forte no subsequente.
- O subsequente EaD evade **menos** que o subsequente presencial. Isso merece atenção na análise, pela possível diferença de perfil dos ingressantes.

**Estrutura para os efeitos fixos cruzados (H1a):**
- 563 de 624 unidades têm ≥ 2 cursos técnicos (média de 3,6).
- 107 de 140 cursos são ofertados em ≥ 2 unidades, e esses cursos somam **99% das matrículas**.
- → **FE de campus × ciclo e curso × ciclo são viáveis.**

**EaD (H2):**
- 111 ofertas, 270 ciclos, 13.842 matrículas por safra, em 24 instituições.
- **56% das matrículas EaD estão em Gestão e Negócios**, seguida de Informação e Comunicação (14%).
- Só 35 cursos EaD, 14 deles em ≥ 2 unidades.
- → Com 6 a 7 safras (edições 2018–2024) há cerca de 700 a 800 ciclos EaD, suficientes para estimar a interação `Q × EaD`. A variação, porém, vem concentrada em poucos eixos. **H2 deve ter seu efeito mínimo detectável calculado antes do pré-registro**; se for alto, H2 vira hipótese secundária.
- Gestão e Negócios, o maior eixo EaD, **não tem CBO no CNCT** (Administração). Isso reforça o mapa por texto (T) como principal.

**Casamento PNP ↔ CNCT:** 132 de 140 nomes de curso casam por nome normalizado ou nomenclatura anterior, cobrindo **99,6% das matrículas**. Sobram 8 nomes, como Análises Químicas e "Análise e Desenvolvimento de Sistemas" (registro inconsistente); vão para `data/reference/pnp_cnct_overrides.csv`.

**Qualidade dos dados:** nos JSON, os campos `Região` e `Município` estão deslocados (trazem a instituição e a região). **Usar o CSV.**

## 8. Série da PNP (edições 2018–2023)

As 6 edições têm as **mesmas 54 colunas**. Cada edição reúne os ciclos com término previsto no ano anterior.

| Edição | Safra (fim previsto) | Matrículas técnicas | Matrículas técnicas EaD | Ofertas técnicas | Ofertas EaD | Evasão técnica |
|---|---|---|---|---|---|---|
| 2018 | 2017 | 193.343 | 75.684 | 3.076 | 770 | — (categorias diferentes) |
| 2019 | 2018 | 143.223 | 6.415 | 2.634 | 50 | 43,9% |
| 2020 | 2019 | 151.437 | 9.950 | 2.722 | 93 | 42,9% |
| 2021 | 2020 | 155.756 | 15.506 | 2.871 | 114 | 38,2% |
| 2022 | 2021 | 149.674 | 9.696 | 2.857 | 93 | 41,4% |
| 2023 | 2022 | 145.831 | 13.842 | 2.752 | 111 | 41,3% |

**Harmonização necessária:**
- **2018** usa as categorias `Conclusão / Evasão / Retidos` e **não tem código de ciclo** (100% "Não Informado"). O ciclo terá de ser reconstruído por unidade × curso × datas de início e fim.
- **2023** separa `Concluídos` de `Concluintes`; as duas contam como conclusão.
- **EaD em 2018:** 75 mil matrículas e 770 ofertas, provavelmente o encerramento dos ciclos da Rede e-Tec Brasil. Isso é uma quebra estrutural; a EaD de 2018 entra numa análise de sensibilidade (com e sem ela).

**Total disponível:** cerca de 940 mil matrículas técnicas em 6 safras (2017–2022). Sem 2018 restam cerca de 56 mil matrículas EaD e cerca de 460 ciclos/ofertas EaD.

**RAIS necessária:** ciclos de até 4 anos que terminam entre 2017 e 2022 começam a partir de cerca de 2013, e `Q` é medido no ano anterior ao início. A RAIS precisa cobrir **2012–2022** (2023–2024 para as safras seguintes).

## 9. Poder estatístico: efeito mínimo detectável (MDE)

Simulação exigida pela spec 04 antes do pré-registro. Código em `tcc_aderencia.models.power`, sobre a tabela de ciclos de `tcc_aderencia.ingest.pnp.load_cycles`.

**Desenho: injeção de efeito.** Mantêm-se a estrutura real (18.393 ciclos técnicos das edições 2019–2023, 920 deles EaD, com matrículas, campus, curso e território) e o **desfecho real**. `Q` é **sorteado** N(0,1) por região imediata × curso, constante entre ciclos, como na RAIS (corr. 0,93). Como `Q` é aleatório, nenhum efeito real é estimado, o que é compatível com o pré-registro. Estimação: LPM ponderado por matrículas, com `Q` e `Q×EaD`, FE de campus × edição e curso × edição, EP agrupado por região imediata, 1.000 sorteios, α = 0,05 e poder de 80%. A edição 2018 fica de fora, por não ter código de ciclo.

**MDE em pontos percentuais por 1 dp do componente idiossincrático de Q** (território × curso, o que sobra após os FE). Os valores usam o valor crítico corrigido pelo tamanho empírico do teste:

| Especificação | Desfecho | H1a (β₁) | H2 (β₃, Q×EaD) | Tamanho nominal 5% do teste de H2 |
|---|---|---|---|---|
| FE campus×t + curso×t | evasão | 0,80 | **4,65** | 10,0% |
| FE campus×t + curso×t | conclusão | 1,00 | **4,27** | 7,9% |
| FE campus×modalidade×t + curso×t | evasão | 0,79 | **5,34** | 15,4% |
| FE campus×modalidade×t + curso×t | conclusão | 0,98 | **3,18** | 9,3% |

**Leitura:**
- **H1a tem poder com folga.** Detecta efeitos de cerca de 1 p.p. por dp de Q, sobre uma evasão média de 41%, e o teste tem tamanho correto (5,9–6,7%).
- **H2 só detecta diferenças de inclinação EaD × presencial de 4 a 5 p.p. por dp de Q.** É um efeito grande para a literatura de mercado local. Se só uma fração `f` da variância de Q for idiossincrática, o MDE por dp de Q cresce em 1/√f (com f = 0,5, fica em ≈ 6–7,5 p.p.). → **H2 deve ser secundária** no pré-registro, ou ser declarada com o MDE explícito.
- **O EP agrupado é anticonservador para H2.** A EaD está em 97 de 372 regiões imediatas, e 5 delas concentram 48% das matrículas EaD, então há poucos clusters efetivos. → Pré-registrar **bootstrap selvagem por cluster** ou **inferência por randomização** para H2 (pendência P15).
- Os números serão refeitos com o Q real (após a RAIS e o classificador), que só mexe na escala (fração f), não na estrutura.

## Arquivos gerados
- `data/external/cnct4_cursos.csv`, `cnae_subclasses.csv`, `ibge_municipios_rgi.csv`
- `data/interim/rais_norte_{2019,2024}_mun_cnae_cbo.parquet`, `rais_norte2024_cnae_cbo.parquet`, `map_O_norte2024.parquet`
