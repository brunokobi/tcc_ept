# Prospecção inicial dos dados — relatório de viabilidade

Data: 18/11/2026. Objetivo: verificar, com dados reais, se o plano das specs é executável antes de investir no pipeline completo.

## Resumo

| Fonte | Status | Veredito |
|---|---|---|
| CNCT 4ª ed. | baixado e processado | **viável** |
| CNAE 2.3 | baixado (API IBGE) | **viável** |
| IBGE (RGI/RGInt) | baixado | **viável** |
| RAIS vínculos | amostra Norte 2019 e 2024 processada | **viável** |
| Ponte CBO (caminho O) | testada na amostra | **viável como validação, não como mapa principal** |
| Variação temporal da aderência | medida na amostra | **muda o desenho de H1a** |
| PNP microdados | **pendente** — portal do MEC atrás de verificação anti-robô; download manual pelo pesquisador | a verificar |

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

## 7. PNP (pendente)
Perguntas a responder assim que os arquivos forem baixados:
1. **Volume de ofertas técnicas EaD** por ano e por eixo (poder para H2).
2. **Ciclos completos por oferta** no arquivo de eficiência acadêmica (série desde a PNP 2018).
3. **Campi com ≥ 2 cursos e cursos em ≥ 2 campi** (requisito dos FE cruzados de H1a).
4. **Localização:** a documentação de 2020 indica só o município da unidade de ensino; confirmar se existe polo ou residência nas edições recentes (P1).
5. **Mudança de estrutura em 2024** (ofício SETEC 81/2024): harmonização da série.
6. **Casamento curso PNP ↔ CNCT** (nomes; cursos com nomenclatura anterior).

## Arquivos gerados
- `data/external/cnct4_cursos.csv`, `cnae_subclasses.csv`, `ibge_municipios_rgi.csv`
- `data/interim/rais_norte_{2019,2024}_mun_cnae_cbo.parquet`, `rais_norte2024_cnae_cbo.parquet`, `map_O_norte2024.parquet`
