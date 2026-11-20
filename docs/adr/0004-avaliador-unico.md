# ADR-0004 — Amostra de referência com avaliador único (por ora)

- **Status:** proposta
- **Data:** 2026-11-20

## Contexto
A spec 02 prevê dois avaliadores humanos para a amostra de referência CNAE → eixo (300 subclasses, `data/reference/gold_v1.csv`), com alfa de Krippendorff entre eles. No momento não há segundo avaliador disponível (P12). A anotação é o gargalo do cronograma: ela destrava o ajuste do classificador T (marco G2), o índice Q e o pré-registro (G3).

## Decisão
1. O pesquisador anota sozinho a planilha `annotation/anotacao_avaliador_A.xlsx`, **primeiro o split dev (99 subclasses)** e depois o teste (201). O ajuste do classificador usa só o dev.
2. A confiabilidade é medida **intra-avaliador**: reanotação cega de 20% da amostra após ≥ 4 semanas (`annotation/PROTOCOLO.md`, passo 4), com alfa de Krippendorff entre as duas rodadas.
3. Se surgir um segundo avaliador antes do pré-registro, ele anota uma subamostra do teste (~100 subclasses, sorteio com seed fixa), e o alfa inter-avaliador é reportado nela.
4. Classificações por LLM (spec 02, etapa 3) podem ser comparadas com a anotação como **medida auxiliar** de concordância, mas **nunca entram no gabarito**.
5. A ausência de segundo avaliador (se persistir) é declarada como limitação no pré-registro e no artigo.

## Alternativas consideradas
- **Esperar o segundo avaliador:** atrasa G2 e G3 por tempo indeterminado.
- **LLM como segundo avaliador:** contamina a validação, porque o próprio classificador T usa LLM; seria comparar o método com ele mesmo.
- **Reduzir a amostra:** diminui o poder das métricas por eixo (13 eixos), sem resolver a falta de um segundo avaliador.

## Consequências
- O alfa reportado é de estabilidade (intra), que não captura viés sistemático do pesquisador; isso é declarado.
- O gabarito do dev fica disponível semanas antes, o que permite ajustar o classificador em paralelo com a anotação do teste.
- A spec 02 continua válida no restante; a P12 segue aberta, mas deixa de bloquear o cronograma.
