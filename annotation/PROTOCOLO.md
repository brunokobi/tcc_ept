# Protocolo de anotação CNAE → eixo CNCT

1. Para cada subclasse em `data/reference/gold_v1.csv`, ler descrição e notas explicativas da CNAE.
2. Atribuir **eixo principal** (1 dos 13) e, se houver, **eixos secundários**; marcar `nao_se_aplica` quando nenhum curso técnico forma para a atividade.
3. Registrar dúvidas em `nota`. Não consultar a saída do classificador durante a anotação.
4. Após ≥ 4 semanas, reanotar 20% (sorteio com seed fixa, `scripts/sample_reannotation.py`) em `gold_v1_reanotacao.csv`, sem olhar a primeira anotação.
5. Dividir dev/teste (seed fixa) **antes** de qualquer ajuste do classificador.
