# Spec 03 — Índices de aderência (v2)

Notação: oferta *o* do curso *c* no território *r*; ciclo que começa no ano *t₀* e termina em *t₁*; `E(r,s,t)` = vínculos RAIS da subclasse *s* no território *r* no ano *t*; `w(s,c)` da spec 02.

## Q — aderência estrutural (H1a, H2)
Emprego ligado ao curso: `L(r,c,t) = Σ_s w(s,c)·E(r,s,t)`.
Participação: `P(r,c,t) = L(r,c,t) / Σ_s E(r,s,t)`.
**Principal:** quociente locacional `Q(o) = P(r,c,t₀−1) / P(Brasil,c,t₀−1)` (ano anterior ao ingresso), em log.
Motivo: participação bruta mede urbanização em eixos como Gestão e Informação; o QL compara com o país.

## S — choque de demanda durante o ciclo (H1b)
`S(o) = ln L(r,c,t₁) − ln L(r,c,t₀)` (crescimento do emprego ligado ao curso no território durante o ciclo).

## B — instrumento shift-share para S
`B(o) = Σ_s z(r,c,s) · g₋ᵣ(s, t₀→t₁)`, com `z = w(s,c)·E(r,s,t₀−1) / L(r,c,t₀−1)` (ADR-0005)
- `z`: participação da subclasse no emprego ligado ao curso no território, no ano base (t₀−1)
- `g₋ᵣ = ln E₋ᵣ(s,t₁) − ln E₋ᵣ(s,t₀)`: crescimento nacional do emprego da subclasse excluindo o território *r* (leave-one-out)
- Diagnósticos de Goldsmith-Pinkham et al. (pesos de Rotemberg) e Borusyak et al. (choques como unidade).

## Variantes de robustez
| ID | Variante |
|---|---|
| R1 | participação bruta `P` em vez de QL |
| R2 | mapeamento O (CBO) em vez de T (texto) |
| R3 | nível eixo em vez de curso |
| R4 | estabelecimentos CNPJ em vez de vínculos |
| R5 | território = região intermediária; = município da unidade |
| R6 | CNCT 5ª edição (se oficial) |

## Implementação
`index/aderencia.py` (`territory_employment`, `linked_employment`, `cycle_indices`, `shift_share`) e `scripts/build_indices.py`. Q indefinido quando L = 0: ver ADR-0005.

## Saída
`data/processed/indices.parquet`: `oferta_id, ciclo_id, territorio, curso, Q, S, B, R1..R6`.

## Testes
P ∈ [0,1]; Σ_c P ≤ 1 quando `Σ_c w(s,c) ≤ 1`; QL nacional = 1; casos-sentinela (Agropecuária em RGI agrícola > 1).
