# ADR-0001 — Edição do CNCT usada pelo classificador

- **Status:** proposta
- **Data:** 2026-11-18

## Contexto
A PNP registra cursos sob a nomenclatura vigente em cada ano (4ª edição do CNCT e anteriores). A 5ª edição passou por consulta pública em 2026 (197 cursos revisados em 13 eixos).

## Proposta
Usar a **4ª edição** como principal (coerente com a série histórica da PNP) e a 5ª como **análise de robustez** (variante A6), via tabela de correspondência 4ª↔5ª em `data/reference/cnct_4_5_crosswalk.csv`.

## Alternativas
- Só 5ª: mais atual, mas descasada dos cursos já ofertados.
- Ambas em paralelo no classificador: dobra o custo de anotação.

## Consequências
Precisa de crosswalk 4ª↔5ª; decidir com o orientador (pendência P2).
