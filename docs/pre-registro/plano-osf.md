# Pré-registro (rascunho para o OSF)

> Modelo: OSF Preregistration, dados secundários. Rascunho v2 de 2026-11-20, a revisar com o orientador. Nenhum efeito foi estimado. Pendências que precisam fechar antes de registrar: P20 (segunda passada do LLM, opcional), ADR-0004 e ADR-0005 (aceite), P2 (edição do CNCT).

## 1. Título e autores
*Aderência territorial dos cursos técnicos da Rede Federal e evasão: presencial × EaD*. Bruno Kobi (IFSul), orientação: _(nome)_.

## 2. Hipóteses (spec 00)
Desfecho principal: **evasão** do ciclo. Desfecho secundário: **conclusão**.
- **H1a (pertencimento):** maior aderência estrutural Q → menor evasão (β₁ < 0) e maior conclusão.
- **H1b (custo de oportunidade):** choque de demanda S durante o ciclo → maior evasão (β₂ > 0), mais forte em cursos subsequentes (β₄ > 0).
- **H2 (modalidade):** a associação de Q com a evasão é mais fraca na EaD (β₃ > 0). **Secundária**, pelo poder limitado (seção 8).

## 3. Dados
- **PNP, eficiência acadêmica, edições 2018–2023:** cada ciclo aparece uma vez, na edição seguinte ao fim previsto, com a situação final das matrículas. Ciclos técnicos de 2011 a 2022 somam 22.316 ciclos, 1.855 deles EaD. Em 2018 o código do ciclo foi reconstruído (spec 01).
- **RAIS, vínculos ativos em 31/12, 2012–2025:** agregados por região imediata do IBGE × subclasse CNAE 2.3 (harmonizada) × ano.
- **CNCT 4ª ed.**, mapa CNAE → curso pelo classificador T (spec 02, avaliado no teste: macro-F1 0,83 [0,75; 0,88] contra a referência LLM) e caminho O (CBO) como robustez.
- **Inclusão:** ciclo de curso técnico (integrado, concomitante, subsequente e PROEJA) com curso casado ao CNCT (99,99%), Q definido (L > 0; 89% dos ciclos, ADR-0005) e **≥ 5 matrículas** (exclui 1,5%).

## 4. Conhecimento prévio dos dados
Antes do registro, o pesquisador viu:
- descritivas da PNP (número de ciclos e ofertas, taxas médias de evasão e conclusão);
- totais da RAIS;
- distribuição, cobertura e correlações dos índices Q, S e B entre si e entre variantes (`docs/resultados/indices.json`);
- métricas do classificador;
- simulação de poder com Q **sorteado** e o desfecho real.

Ele **não** viu nenhuma relação entre desfecho e Q, S ou B.

## 5. Variáveis
- **Desfechos:** `evasao` e `conclusao`, proporções do ciclo com denominador nas matrículas.
- **Q** = ln QL(r, c, t₀−1), em que QL é a participação do emprego ligado ao curso no território dividida pela participação nacional. Território = região imediata do campus. Padronizado (dp = 1) na amostra analítica.
- **S** = ln L(r,c,t₁) − ln L(r,c,t₀). **B** = Bartik *leave-one-out* sobre o emprego ligado ao curso (ADR-0005).
- **EaD** = modalidade da oferta. **Subsequente** = tipo de oferta.
- **Controles X:** ln(matrículas do ciclo) e duração prevista do ciclo em anos. Território, campus e curso entram pelos efeitos fixos.

## 6. Modelos (spec 04)
- **H1a e H2:** logit fracionário ponderado por matrículas, `Λ(β₁Q + β₃Q×EaD + γX + δ_campus×t + η_curso×t)`, com t = ano de início. LPM com os mesmos efeitos fixos (linearmodels) como espelho.
- **H1b:** `Λ(β₂S + β₄S×Subsequente + γX + α_oferta + τ_t)`. Oferta = campus × curso × modalidade. Modelo principal em 2SLS linear com B instrumentando S; reportar F de primeiro estágio (Montiel Olea–Pflueger), pesos de Rotemberg e teste de choques (Borusyak et al.).
- Oferta com um único ciclo não contribui para H1b (efeito fixo de oferta).

## 7. Inferência
- α = 0,05, bicaudal.
- Holm entre H1a, H1b e H2 no desfecho evasão. A conclusão é reportada como secundária, com Holm separado.
- **Erros agrupados por região imediata.** Para H2: **bootstrap selvagem por cluster** (Webb, 9.999 réplicas) e p-valor de **inferência por randomização** (permutação da EaD entre ofertas do mesmo campus) (P15).
- Critério para H2: β₃ > 0 com p de Holm < 0,05 pelo bootstrap selvagem. Um resultado nulo é interpretado à luz do MDE.

## 8. Poder (efeito mínimo detectável a 80%)
Simulação por injeção de efeito com a estrutura real (relatório de viabilidade, §9). A fração idiossincrática do Q real (variância que sobra após os efeitos fixos de campus × t e curso × t) é **f = 0,39** (0,38 no caminho O; 0,39 por eixo). O MDE por 1 dp de Q fica:

| Hipótese | Evasão (p.p.) | Conclusão (p.p.) |
|---|---|---|
| H1a | 1,3 | 1,6 |
| H2 (diferença de inclinação EaD) | 7,4 | 6,8 |

## 9. Robustez (spec 03)
| ID | Variante |
|---|---|
| R1 | Participação bruta (ln P) |
| R2 | Caminho O (CBO) |
| R3 | Nível de eixo |
| R5 | Território = região intermediária |
| R-zero | Ciclos com L = 0 incluídos com ln(QL + ε) + dummy (ADR-0005) |
| R-2019 | Sem os ciclos de DF e SE que usam a RAIS 2019 (P16) |
| R-conf | Só subclasses com consenso entre os dois LLMs |

Placebos (spec 04):
- território sorteado em outra UF (1.000 sorteios);
- Q de curso de outro eixo;
- S do ciclo seguinte (pré-tendência).

Seleção da oferta: comparação descritiva de Q entre territórios com e sem oferta, por eixo.

## 10. Exploratório (rotulado como tal)
- Heterogeneidade por eixo, região e tipo de oferta (Benjamini–Hochberg).
- Estudo de evento.
- SHAP.

## 11. Dados faltantes e outliers
- Ciclos sem Q, sem S ou sem B saem só das análises que usam o índice.
- Reportar a comparação das características observáveis dos ciclos excluídos.
- Sem *winsorização* dos desfechos (proporções). S e B são *winsorizados* a 1%/99% como sensibilidade, não no modelo principal.

## 12. Desvios
Registrar em `docs/pre-registro/desvios.md`.

Link OSF: _(após registro)_
