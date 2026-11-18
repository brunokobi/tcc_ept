# ADR-0002 — Unidade territorial

- **Status:** aceita (18/11/2026, após prospecção da PNP)
- **Data:** 2026-11-18

## Contexto
O território precisa representar o mercado de trabalho de referência do estudante. Na EaD, o aluno pode morar longe do campus/polo (pendência P1).

## Proposta
- Principal: **região geográfica imediata (IBGE 2017)** do campus (presencial) ou do **polo** (EaD), se a PNP informar o polo; senão, do campus.
- Robustez: região intermediária e município (variante A5).
- Se a PNP trouxer município de residência agregado, usar distribuição de residência como ponderação do território na EaD.

## Consequências
Resultado de H2 depende de P1; documentar a escolha no pré-registro.

## Atualização após a prospecção
Os microdados da PNP (2023) só trazem o município da unidade; as ofertas EaD estão registradas na unidade, sem polo nem residência. Decisão: **território = região imediata do município da unidade, para as duas modalidades**. H2 é interpretada como diferença no vínculo com o território da unidade.
