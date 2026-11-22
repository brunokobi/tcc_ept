# ADR-0006 — Página pública de resultados descritivos antes do G4

- **Status:** aceita (decisão do pesquisador em 2026-11-22)
- **Data:** 2026-11-22

## Contexto
A spec 05 prevê o produto técnico (painel, MCP, chat) só depois do G4, quando os resultados principais estiverem fechados. Antes do pré-registro, o pesquisador precisava mostrar ao orientador o estado do projeto: classificador, índices, poder e revisão. Os resultados descritivos já existem (`docs/resultados/`) e não envolvem desfechos.

## Decisão
1. Publicar uma **página estática e só descritiva** em https://tccept.brunokobi.tech (vpsrafa, container `tccept-web`), gerada por `scripts/make_figures.py` e publicada por `scripts/deploy_pagina.sh`. O código-fonte fica em `reports/pagina/index.html`.
2. A página mostra só: métricas do classificador, mapa do Q por curso, convergência T × O, distribuições de Q, S e B, sentinela, MDE e o fluxo PRISMA.
3. **Nenhum gráfico ou número relaciona evasão ou conclusão a Q, S ou B** até o registro no OSF. `make_figures.py` descarta as colunas de desfecho ao carregar o painel.
4. O painel da spec 05 (com evasão, conclusão e filtros) continua sendo extensão pós-G4. Esta página não o substitui.

## Alternativas consideradas
- **Só o link privado do Claude:** exige compartilhar conta por conta; preterido pelo pesquisador.
- **Página com senha:** possível no Traefik; preterida porque o conteúdo é público e agregado.
- **Esperar o G4:** o orientador ficaria sem visão do projeto na decisão do pré-registro.

## Consequências
- A página é pública: qualquer atualização antes do OSF precisa manter a regra do item 3.
- Os números exibidos já constam do pré-registro (seção 4, conhecimento prévio); a página não amplia o que o pesquisador viu dos dados.
- Para atualizar: `python scripts/make_figures.py` e `TCCEPT_SSH_KEY=<chave> scripts/deploy_pagina.sh`.
