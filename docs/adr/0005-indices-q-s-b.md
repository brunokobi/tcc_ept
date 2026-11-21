# ADR-0005 — Definições operacionais de Q, S e B

- **Status:** proposta (fechar antes do pré-registro); item 3 executado em 2026-11-21
- **Data:** 2026-11-20

## Contexto
A spec 03 define Q, S e B, mas três pontos só apareceram ao calcular os índices com os dados reais (`scripts/build_indices.py`, resultados em `docs/resultados/indices.json`):

1. **Pesos do instrumento B.** A fórmula da spec 03 multiplica `π(r,s)` (participação da subclasse no emprego total do território) por `w(s,c)/Σ_s w(s,c)`. Essa combinação não soma 1 entre subclasses e não prediz o crescimento de `L(r,c)`, que é o que `S` mede.
2. **Q indefinido quando L = 0.** `Q = ln QL` não existe quando o território não tem nenhum emprego ligado ao curso. Isso acontece em 2.465 de 22.316 ciclos (11%).
3. **O w_T é esparso.** O LLM atribui a cada subclasse um eixo e um ou poucos cursos. Por isso, 13 cursos ofertados não recebem nenhuma subclasse (Automação Industrial, Biotecnologia, Qualidade, Produção de Moda e outros). Para esses cursos, L = 0 em todo o país.

## Decisão
1. **B usa o Bartik padrão sobre o emprego ligado ao curso:** `B = Σ_s z(r,c,s)·g₋ᵣ(s)`. Aqui `z = w(s,c)·E(r,s,t₀−1) / L(r,c,t₀−1)` é a participação de cada subclasse no emprego ligado ao curso no território, no ano base, e `g₋ᵣ = ln E₋ᵣ(s,t₁) − ln E₋ᵣ(s,t₀)` é o crescimento nacional da subclasse fora do território (*leave-one-out*). Assim, `B` é o crescimento previsto de `L(r,c)` se cada subclasse local crescesse como no resto do país, e é diretamente comparável a `S`. Subclasses com `E₋ᵣ = 0` em t₀ ou t₁ ficam de fora, e z é renormalizado.
2. **Análise principal só com L > 0** (Q definido). Na sensibilidade, os ciclos com L = 0 entram com `Q = ln(QL + ε)`, sendo ε o menor QL positivo do curso no ano, e uma dummy indica L = 0. Os 13 cursos sem nenhuma subclasse em w_T ficam fora de H1a e H2, ou entram pela variante R3 (eixo).
3. **Antes do pré-registro, rodar uma segunda passada do LLM**, recomendada e registrada em P20. Para cada subclasse, o LLM lista **todos** os cursos do CNCT (de qualquer eixo) que formam para a atividade, com pesos, como prevê o JSON `{eixo, cursos, peso}` da spec 02. O eixo principal já avaliado no teste (G2) não muda. Se essa passada não for feita, vale o item 2 e a limitação é declarada.

## Alternativas consideradas
- **Fórmula literal da spec 03 para B:** descartada pelo motivo do item 1 do Contexto.
- **Q = asinh(QL) ou ln(QL + 1) como principal:** muda a escala e mistura a margem "zero" com a intensiva. Fica só como sensibilidade.
- **Usar w_O para os cursos sem w_T:** mistura os dois caminhos que deveriam ser independentes e invalida a comparação T × O.

## Consequências
- A spec 03 passa a citar esta ADR na definição de B.
- Antes da segunda passada, a cobertura da análise principal era de 89% dos ciclos (80% dos EaD); ver a atualização abaixo. Pré-registrar a cobertura e comparar as características dos ciclos excluídos.
- **Atualização de 2026-11-21: segunda passada executada** (`scripts/run_course_weights.py`, ERNIE, 1.265 subclasses, média de 4,7 cursos por subclasse; o eixo principal aparece em 99,8% delas). Agora 188 dos 189 cursos civis têm alguma subclasse; só Tradução e Interpretação de Libras ficou sem nenhuma. Resultados:
  - cobertura de Q de 89% para **98% dos ciclos** (EaD: de 80% para **96%**), com L = 0 em 364 ciclos;
  - convergência T × O nos ciclos: Spearman de 0,60 para **0,65** (S: de 0,42 para 0,53; mediana por curso: de 0,47 para 0,59);
  - Spearman entre S e B de 0,33 para 0,42;
  - fração idiossincrática de Q: f = 0,38.

  O w_T do mapa final é o multicurso (`metodo_T = llm_multicurso`). O item 2 (L = 0) continua valendo para os 364 ciclos restantes.
