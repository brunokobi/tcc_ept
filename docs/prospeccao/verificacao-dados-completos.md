# Verificação final de viabilidade: todos os dados

Data: 19/11/2026. Complementa o [relatório de viabilidade](relatorio-viabilidade.md), que testou amostras (RAIS do Norte, PNP 2023). Aqui, todas as fontes do núcleo do projeto foram baixadas e verificadas em escala nacional.

Reprodução: `python -m tcc_aderencia.ingest.rais <ano>` para 2012–2025, seguido de `python scripts/verify_data.py`. Resultados brutos em [`verificacao-dados-completos.json`](verificacao-dados-completos.json).

> Verificação **apenas descritiva**. Nenhum modelo de efeito foi estimado (regra do pré-registro). O `Q` usado aqui é o do **mapa O** (ponte CBO), que é a validação; o mapa principal (T, texto com IA) ainda não existe.

## Veredito

| Fonte / requisito | Veredito | Evidência |
|---|---|---|
| RAIS 2012–2025 | ✅ **viável** | 214 arquivos (37 GB), 14 anos agregados; totais iguais ao estoque oficial (diferença < 0,03%), exceto 2019 |
| Chaves RAIS (município, CNAE, CBO) | ✅ **viável** | 100% dos municípios casam com o IBGE; CNAE fora da lista 2.3 ≤ 1,2%; CBO inválido ≤ 0,14% |
| PNP 2019–2023 | ✅ **viável** | 18.393 ciclos técnicos, 920 deles EaD; 100% com território |
| PNP ↔ CNCT | ✅ **viável** | 99,85% das matrículas casam por nome ou nomenclatura anterior |
| Ponte CBO (mapa O) | ✅ viável como validação | ~19% dos vínculos estão em CBOs de cursos; 366–374 das 374 CBOs aparecem |
| Q com cobertura da PNP | ⚠️ **parcial no mapa O** | 82,5% das matrículas têm Q; **só 58% das matrículas EaD** (Administração e Gestão não têm CBO no CNCT) → o mapa T é indispensável para H2 |
| Variação de Q para H1a | ✅ **suficiente** | dp de log Q ≈ 0,82; 57% da variância sobra após os FE de território e curso |
| Variação de S para H1b | ✅ **suficiente** | dp de Δ log Q em 5 anos ≈ 0,34 (Norte: 0,26) |
| Poder de H1a | ✅ **com folga** | MDE ≈ 1,1 p.p. de evasão por 1 dp de Q |
| Poder de H2 | ⚠️ **limitado** | MDE ≈ 4,2–7,1 p.p. por 1 dp de Q, e o EP agrupado é anticonservador → hipótese secundária, com inferência robusta (P15) |
| PNP 2024–2025 | ⚠️ incerto | não publicada no mesmo formato (P5); o projeto segue com 2017–2022 |

**Conclusão: o projeto é viável.** Todas as fontes do núcleo (RAIS, PNP, CNCT, CNAE, IBGE) estão disponíveis, completas e com chaves que casam. H1a e H1b têm variação e poder suficientes. Os riscos são de desenho, não de dados:
1. H2 tem poder limitado e poucos clusters;
2. o mapa O cobre mal a EaD, o que torna o mapa T obrigatório;
3. o total de 2019 precisa ser conferido.

## 1. RAIS: totais e qualidade das chaves

| Ano | Vínculos ativos (mi) | Oficial MTE (mi) | Diferença | CNAE fora da 2.3 | CBO inválido |
|---|---|---|---|---|---|
| 2012 | 47,459 | 47,459 | −0,001% | 1,09% | 0,07% |
| 2013 | 48,948 | 48,948 | +0,001% | 1,13% | 0,12% |
| 2014 | 49,572 | 49,572 | −0,001% | 1,16% | 0,12% |
| 2015 | 48,061 | 48,061 | −0,000% | 0,58% | 0,13% |
| 2016 | 46,060 | 46,060 | +0,000% | 0,59% | 0,13% |
| 2017 | 46,282 | 46,282 | −0,001% | 0,59% | 0,13% |
| 2018 | 46,631 | 46,632 | −0,002% | 0,00% | 0,12% |
| **2019** | **46,716** | **47,555** | **−1,76%** | 0,00% | 0,00% |
| 2020 | 46,236 | 46,236 | +0,000% | 0,00% | 0,00% |
| 2021 | 48,729 | 48,728 | +0,002% | 0,00% | 0,01% |
| 2022 | 52,791 | 52,777 | +0,026% | 0,01% | 0,00% |
| 2023 | 55,818 | — | — | 0,00% | 0,00% |
| 2024 | 57,801 | — | — | 0,01% | 0,00% |
| 2025 | 60,692 | — | — | 0,01% | 0,00% |

- Os valores oficiais são os totais divulgados pelo MTE, digitados no script (`OFFICIAL_STOCK_MI`). Para 2023+ não foi usada referência.
- **Critério de aceite da spec 01 (±1% por UF):** atendido no total nacional em 13 dos 14 anos.
- **2019:** os 6 arquivos regionais estão presentes e com totais plausíveis (Centro-Oeste e Nordeste abaixo de 2018 e de 2020). A diferença é dos microdados públicos ou da referência usada. Fica pendente conferir com a tabela do PDET e rodar uma sensibilidade sem 2019 (P16).
- **CNAE fora da 2.3 até 2017:** são subclasses da CNAE 2.0 descontinuadas, ~1% dos vínculos. Precisam de tabela de correspondência 2.0 → 2.3 antes do classificador (P17).
- **Correção feita nesta verificação:** o layout de 2023+ grava o CBO sem o zero à esquerda (`010310` → `10310`, família 0 = Forças Armadas). O `rais.py` agora completa o código com zeros até 6 dígitos (`lpad`), e 2023–2025 foram reagregados. Não afeta Q, porque nenhum curso civil usa a família 0.
- Processamento: ≈ 3 h de download (4 e depois 8 conexões, com uma queda de internet no meio) e 2–18 min de agregação por ano; o agregado tem ≈ 300 MB.

## 2. Ponte CBO e cobertura de Q

- Entre 18,7% e 19,4% dos vínculos estão em CBOs de algum curso técnico, estável na série.
- Das 374 CBOs (ou famílias) dos cursos civis, 366 a 374 aparecem na RAIS em todos os anos.
- O CNCT lista para alguns cursos a **família** CBO de 4 dígitos (por exemplo, Informática: `3171;3172`), então o casamento é por prefixo.

**Cobertura da PNP (ciclos de 2019–2023, Q medido 4 anos antes do fim previsto):**
- 99,85% das matrículas têm curso casado no CNCT. Ficam de fora cursos residuais: aeronáutica, infantaria e "Análise e Desenvolvimento de Sistemas", que é registro inconsistente de curso superior.
- **82,5% das matrículas têm Q pelo mapa O; na EaD, 58%.** O que falta é sobretudo Administração e outros cursos de Gestão e Negócios, sem CBO no CNCT, justamente o maior eixo da EaD. Isso **confirma que o mapa T (CNAE → eixo por texto) é necessário** para H2.

## 3. Variação e estabilidade de Q (mapa O, região imediata × curso)

| | 2012 | 2016 | 2020 | 2025 |
|---|---|---|---|---|
| Células (> 50 vínculos ligados) | 13.776 | 14.161 | 14.357 | 16.838 |
| dp de log Q | 0,85 | 0,83 | 0,84 | 0,80 |
| Fração f não explicada por FE de território + curso | 0,56 | 0,56 | 0,57 | 0,61 |

| Janela | Pares | Corr. de log Q | dp de Δ log Q (S) |
|---|---|---|---|
| 2012–2017 | 12.470 | 0,91 | 0,34 |
| 2016–2021 | 13.009 | 0,92 | 0,32 |
| 2020–2025 | 13.715 | 0,91 | 0,34 |

- Os resultados confirmam a prospecção em escala nacional. Q é estável (corr. ≈ 0,91 em 5 anos), então **o FE de oferta não identifica H1a** e o desenho transversal com FE cruzados (spec 04) se mantém.
- **S varia mais do que no Norte** (dp 0,34 contra 0,26), o que é bom para H1b.

## 4. Poder estatístico com a variação real de Q

O MDE da §9 do relatório de viabilidade é por 1 dp do componente **idiossincrático** de Q. Com a fração mediana f = 0,567, o MDE por 1 dp de Q é MDE / √f:

| Especificação | Desfecho | H1a | H2 (Q×EaD) |
|---|---|---|---|
| FE campus×t + curso×t | evasão | **1,06 p.p.** | **6,2 p.p.** |
| FE campus×t + curso×t | conclusão | 1,33 p.p. | 5,7 p.p. |
| FE campus×modalidade×t + curso×t | evasão | 1,05 p.p. | 7,1 p.p. |
| FE campus×modalidade×t + curso×t | conclusão | 1,30 p.p. | 4,2 p.p. |

(Evasão média: 41% no presencial, 43% na EaD, ciclos de 2019–2023.)

- **H1a:** detecta cerca de 1 p.p. por dp de Q. Com dp de log Q ≈ 0,8, é um efeito pequeno e plausível. **Poder adequado.**
- **H2:** só detecta diferenças de 4 a 7 p.p. na inclinação EaD × presencial por dp de Q, além de o teste ter tamanho de 8–15% com EP agrupado. **Recomendação para o pré-registro:** H2 como hipótese **secundária**, com MDE declarado e inferência por bootstrap selvagem por cluster ou randomização (P15).

## 5. Pendências abertas por esta verificação
- **P16:** total da RAIS 2019 1,76% abaixo do oficial. Conferir no PDET; sensibilidade sem 2019.
- **P17:** ~1% dos vínculos de 2012–2017 com subclasse CNAE 2.0 descontinuada. Correspondência 2.0 → 2.3 (CONCLA) antes do classificador.
- Já existentes e reforçadas: **P5** (PNP 2024+), **P15** (inferência de H2), mapa T obrigatório para a cobertura da EaD.
