# Spec 00 — Visão geral (v2)

## Pergunta
A aderência entre os cursos técnicos da Rede Federal e a estrutura produtiva do seu território está associada à evasão e à conclusão? Em que direção, por qual mecanismo, e a associação difere entre EaD e presencial?

## Hipóteses (direcionais, pré-registradas)
- **H1a — pertencimento:** maior aderência estrutural `Q` → menor evasão, maior conclusão.
- **H1b — custo de oportunidade:** choque positivo de demanda `S` no setor do curso durante o ciclo → maior evasão; efeito maior em cursos subsequentes e ingressantes mais velhos.
- **H2 — modalidade:** a associação de `Q` com evasão é mais fraca na EaD.

## Objetivos específicos → módulos

| OE | Descrição | Módulo | Spec |
|---|---|---|---|
| 1 | Mapeamento CNAE → curso por texto (IA) e por CBO, validado | `classifier/`, `ingest/rais.py` | 02 |
| 2 | Estrutura produtiva por território (RAIS; CNPJ em robustez) | `ingest/` | 01 |
| 3 | Índices `Q` (estrutural), `S` (choque), `B` (shift-share) | `index/` | 03 |
| 4 | Modelos H1a, H1b, H2 | `models/` | 04 |
| 5 | Dados e código abertos (Zenodo) | — | 06 |

## Escopo
**Núcleo:** specs 01–04 e 06. **Extensões** (só depois do G4): estudo de evento, SHAP, painel/MCP/chat (spec 05).

## Pipeline

```
 RAIS (vínculos: mun × CNAE × CBO × ano) ─┬─► estrutura produtiva (território × CNAE × ano)
 IBGE (RGI) ──────────────────────────────┘          │
 CNCT (cursos, CBO) ─┬─► mapa por CBO  ──┐           │
 CNAE (IBGE) ────────┴─► mapa por texto ─┴─► w(s,c) ─┤
                                                     ▼
 PNP (eficiência acadêmica) ─► ofertas × ciclos ─► índices Q, S, B ─► painel analítico
                                                                         │ [pré-registro OSF]
                                                                         ▼
                                                     models (FE, logit fracionário, IV shift-share, placebos)
```

## Unidade de análise
Oferta (curso × unidade × modalidade × tipo de curso) × ciclo de matrícula (ano de início). Desfechos medidos ao fim do prazo previsto do ciclo (arquivo de eficiência acadêmica).
