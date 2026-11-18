# Spec 04 — Modelagem e identificação (v2)

> **Bloqueado até o pré-registro (G3).** Antes disso: dados simulados ou subamostra exploratória declarada.

## Desfechos
`evasao(o)` e `conclusao(o)` do ciclo, proporções com denominador = matrículas do ciclo.

## Modelo principal — logit fracionário com efeitos fixos cruzados
Prospecção (RAIS Norte 2019×2024): `log Q` tem correlação 0,93 entre anos e só 3,5% da variância é intra-território (células com > 50 vínculos ligados). **FE de oferta não identifica H1a.** `S` varia bem (dp ≈ 0,26 em 5 anos). Por isso H1a e H1b usam fontes de variação diferentes:

**H1a / H2 — variação transversal com FE cruzados**
`E[y(o,t)] = Λ( β₁·Q + β₃·Q×EaD + γ·X + δ_{campus×t} + η_{curso×t} )`
- `δ_{campus×t}` absorve tudo do campus e do território no ciclo (economia local, gestão, demanda geral).
- `η_{curso×t}` absorve tudo do curso no país (dificuldade, prestígio, mercado nacional).
- β₁ vem de: *o mesmo curso tem menos evasão nos campi onde seu setor é relativamente mais forte, comparado aos outros cursos do mesmo campus?* Requer campi com ≥ 2 cursos e cursos ofertados em ≥ 2 campi (verificar na PNP).
- EaD: interação; se poucas ofertas EaD por campus, usar `δ_{campus×modalidade×t}`.

**H1b — variação intra-oferta**
`E[y(o,t)] = Λ( β₂·S + β₄·S×Subsequente + γ·X + α_oferta + τ_t )`, com `S` instrumentado por `B` (abaixo).

Comum: pesos = matrículas; erros agrupados por território; LPM com `linearmodels` como espelho.
**Sinais esperados (evasão):** H1a β₁ < 0; H1b β₂ > 0, β₄ > 0; H2 β₃ > 0.

## IV shift-share para S
2SLS (linear) com `B` como instrumento de `S`; reportar F de primeiro estágio, pesos de Rotemberg e teste de choques (Borusyak et al.).

## Placebos
- Território: Q/S calculados em território sorteado em outra UF (1.000 sorteios) → distribuição nula.
- Eixo: Q/S de curso de outro eixo.
- Pré-tendência: S do ciclo seguinte (futuro) não deve prever evasão do ciclo atual.

## Seleção da oferta
Comparar Q de territórios onde ofertas foram abertas vs. não abertas (por eixo); discutir.

## Poder estatístico (antes do pré-registro)
Simulação com a estrutura real (nº de ofertas, ciclos por oferta, variância intra-oferta de Q e S, distribuição de matrículas): menor efeito detectável a 80% de poder, α = 0,05.

## Múltiplas comparações
Hipóteses primárias: H1a, H1b, H2 (3 testes, Holm). Heterogeneidade: Benjamini–Hochberg, rotulada como exploratória.

## Extensões (pós-G4)
Estudo de evento com aberturas/fechamentos de grandes estabelecimentos (CNPJ), estimador Callaway & Sant'Anna; gradient boosting + SHAP (exploratório).

## Implementação
`models/fractional.py`, `models/panel.py`, `models/shift_share.py`, `models/placebo.py`, `models/power.py`; extensões `models/event_study.py`, `models/shap_analysis.py`.
