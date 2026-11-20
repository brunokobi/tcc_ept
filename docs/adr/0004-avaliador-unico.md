# ADR-0004 — Amostra de referência anotada por LLM (sem avaliador humano, por ora)

- **Status:** proposta (decisão do pesquisador em 2026-11-20; levar ao orientador)
- **Data:** 2026-11-20

## Contexto
A spec 02 prevê dois avaliadores humanos para a amostra de referência CNAE → eixo (300 subclasses, `data/reference/gold_v1.csv`), com alfa de Krippendorff entre eles. No momento não há segundo avaliador (P12), e o pesquisador optou por não anotar ele mesmo nesta fase. A anotação é o gargalo do cronograma: ela destrava o ajuste do classificador T (marco G2), o índice Q e o pré-registro (G3).

Uma primeira versão desta ADR propunha anotação humana por avaliador único; o pesquisador escolheu a alternativa de anotação por LLM.

## Decisão
1. As 300 subclasses são anotadas por um **LLM em contexto** (Claude Opus 5.5, na sessão do Claude Code de 2026-11-20), a partir só de descrição, notas "compreende" e atividades da CNAE e da lista de eixos do CNCT, **sem acesso às saídas dos classificadores** baseline/embeddings para essas subclasses. O anotador é registrado na coluna `anotador` (`llm:claude-opus-5-5`).
2. Esse conjunto é chamado de **referência LLM**, não de gabarito humano, no texto do TCC e do pré-registro.
3. A etapa LLM do classificador T (spec 02, passo 3) **não pode usar o mesmo modelo** que gerou a referência; usa outros provedores, para não comparar o método com ele mesmo.
4. Validação humana mínima continua desejável: se o pesquisador ou um segundo avaliador revisar uma subamostra do teste (~60–100 subclasses, sorteio com seed fixa), reporta-se a concordância humano × referência LLM (alfa de Krippendorff). Isso fica como pendência (P12).
5. A natureza da referência é declarada como **limitação** no pré-registro e no artigo.

## Alternativas consideradas
- **Pesquisador anota do zero:** método mais forte; preterido pelo pesquisador nesta fase por tempo.
- **Anotação assistida (LLM sugere, pesquisador revisa):** gabarito humano com viés de ancoragem; preterida pelo pesquisador.
- **Esperar segundo avaliador:** atrasa G2 e G3 por tempo indeterminado.

## Consequências
- As métricas de F1 medem **concordância com a referência LLM**, não acurácia contra julgamento humano; a interpretação no TCC precisa dizer isso.
- Ganho de prazo: G2 deixa de depender de anotação manual.
- Risco de questionamento pela banca; mitigado pela validação humana de uma subamostra (item 4), pela convergência com o caminho O (independente de texto) e pela transparência desta ADR.
- A reanotação intra-avaliador de 20% perde sentido para um LLM; substituída pelo item 4.
