# Protocolo de anotação CNAE → eixo CNCT

0. **Amostra:** 300 subclasses sorteadas por `scripts/sample_reference.py` (seção CNAE × faixa de emprego na RAIS 2019–2023, seed do projeto), em `data/reference/gold_v1.csv`, com `split` dev/teste já definido e a probabilidade de inclusão de cada subclasse (para ponderar as métricas). Cada avaliador anota a **sua** planilha, de forma independente (**situação atual, ADR-0004:** a referência v1 foi anotada por LLM, coluna `anotador`; revisão humana de subamostra pendente): `annotation/anotacao_avaliador_A.xlsx` (pesquisador) e `anotacao_avaliador_B.xlsx` (segundo avaliador, P12).
1. Para cada subclasse, ler descrição e notas explicativas da CNAE.
2. Atribuir **eixo principal** (1 dos 13) e, se houver, **eixos secundários**; marcar `nao_se_aplica` quando nenhum curso técnico forma para a atividade.
3. Registrar dúvidas em `nota`. Não consultar a saída do classificador durante a anotação.
4. Após ≥ 4 semanas, reanotar 20% (sorteio com seed fixa, `scripts/sample_reannotation.py`) em `gold_v1_reanotacao.csv`, sem olhar a primeira anotação.
5. Dividir dev/teste (seed fixa) **antes** de qualquer ajuste do classificador. Já feito no sorteio: 99 dev e 201 teste.
6. Ao final, calcular a concordância A × B (alfa de Krippendorff), resolver as divergências por consenso e gravar o resultado em `gold_v1.csv`.
