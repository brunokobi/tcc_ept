# Revisão sistemática: busca, triagem e síntese preliminar

> Versão 1, 2026-11-21. Triagem por título e resumo feita por LLM (Claude Opus 5.5), nos moldes da ADR-0004. Precisa ser revisada pelo pesquisador e completada com as bases que exigem acesso manual (seção 5). As afirmações sobre cada estudo vêm só do título e do resumo; o texto completo ainda não foi lido.

## 1. Busca (reproduzível)
- **Base:** OpenAlex (indexa SciELO, periódicos com DOI, BDTD/RCAAP/LA Referencia e repositórios). Script em `scripts/search_literature.py`; registros brutos em `docs/revisao/busca/`.
- **Campo:** título + resumo, publicações de 2008 em diante. Até 200 registros por string, ordenados por relevância (a paginação profunda exige chave da API).
- **Strings:**

| ID | Foco | Na base | Baixados |
|---|---|---|---|
| S1 | (evasão OR permanência OR conclusão…) AND (APL OR território OR mercado de trabalho…) AND (instituto federal OR educação profissional OR curso técnico…) | 384 | 200 |
| S2 | evasão AND (EaD) AND (curso técnico OR instituto federal OR e-Tec…) | 152 | 152 |
| S3 | (dropout OR attrition…) AND (vocational/technical education…) AND (local labor market OR labor demand OR skills mismatch…) | 44 | 44 |
| S4 | (dropout OR enrollment OR attainment…) AND (local labor demand OR Bartik OR shift-share OR labor market shock…) | 82 | 82 |

## 2. Critérios
**Incluir** estudos empíricos ou revisões, de 2008 em diante, que atendam a pelo menos uma das condições:
- **A:** relacionam evasão, permanência ou oferta da EPT técnica brasileira ao território, à estrutura produtiva ou ao mercado de trabalho local;
- **B:** medem evasão ou eficiência na Rede Federal em escala multicampi ou nacional;
- **C:** estudam evasão em cursos técnicos EaD (contexto de H2);
- **D:** estimam o efeito de choques de demanda de trabalho local sobre escolarização ou evasão (mecanismo de H1b e método).

**Excluir:**
- estudos só do ensino superior;
- estudos de caso de um curso ou de um campus sem variável territorial ou de mercado;
- relatos de prática;
- textos sem relação com evasão ou com contexto produtivo;
- duplicatas.

## 3. Fluxo PRISMA

| Etapa | n |
|---|---|
| Registros identificados (4 strings) | 478 |
| Após remover duplicatas | 471 |
| Excluídos pelo título | 405 |
| Resumos avaliados | 66 |
| Excluídos pelo resumo | 23 |
| **Incluídos** | **43** (A 10, B 7, C 12, D 14) |

Detalhe por registro: `docs/revisao/triagem.csv`.

## 4. Síntese preliminar
**A. Território × EPT.** Os estudos brasileiros que ligam evasão ao território ou ao mercado de trabalho são **qualitativos ou locais**:
- Brose e Pereira (2025), subsequentes no RS e desenvolvimento regional;
- Souza e Lima (2026), leitura crítica de território, trabalho e abandono;
- Santos (2026), evasão como expressão das contradições do mercado de trabalho;
- Oliveira Neto (2025), paradoxo entre demanda e evasão no PROEJA Agropecuária;
- Silva (2023), mão de obra no setor sucroenergético e oferta de cursos;
- Hellmann (2016), observatório de indicadores do IFPR para planejar a oferta.

O mais próximo, em método, é Silva et al. (2025). Eles cruzam dados acadêmicos do IFCE com RAIS e CBO, mas o desfecho é a inserção no emprego, não a evasão. **Nenhum estudo encontrado mede a aderência curso × estrutura produtiva do território com dados administrativos em escala nacional e a relaciona à evasão.** Essa é a lacuna do TCC.

**B. Evasão na Rede Federal.**
- Silveira (2017), IFSP;
- Duarte (2019), permanência na Rede;
- Alves (2019), eficiência de cursos técnicos;
- Oliveira e Lima (2026), 10 anos da política de permanência e êxito.

Castro et al. (2020) comparam a eficiência acadêmica de cursos subsequentes EaD e presenciais, de forma descritiva. É o antecedente direto de H2.

**C. EaD técnica.** Predominam:
- levantamentos de causas: Faveret Filho et al., 2019a, b; Coelho et al., 2020; Neves e Moura, 2021; Lima et al., 2021;
- modelos preditivos com dados do AVA: Queiroga et al., 2017, 2018; Tamada, 2022.

O foco é o aluno e a plataforma, não o contexto econômico.

**D. Choques de demanda e escolarização.** Há evidência internacional consistente de que o custo de oportunidade importa:
- von Simson (2014): mercados de trabalho locais e evasão no ensino médio, Noruega;
- Atkin (2012/2016): empregos na indústria exportadora e abandono escolar, México;
- Shah e Steinberg (2015): emprego garantido e escolarização, Índia;
- Carrillo (2019): ciclos do café, Colômbia;
- Manacorda et al. (2010): demanda local, trabalho infantil e escola, Brasil;
- Saad e Fallah (2020);
- Demirci e Poyraz (2024);
- Chuan e Zhang (2025), com instrumentos shift-share.

Isso fundamenta H1b e o uso de Bartik. Bessey e Backes-Gellner (2008) e LaForest (2022) tratam de evasão e escolha na educação profissional.

**Implicação para o TCC:**
- H1b tem base teórica e empírica internacional;
- H1a (pertencimento/aderência) e H2 (EaD) não têm teste quantitativo nacional anterior no Brasil;
- a contribuição é o índice de aderência com mapeamento validado e o desenho pré-registrado.

## 5. Pendências da revisão
1. **Bases com acesso manual:** Portal de Periódicos CAPES (login institucional), BDTD (a API respondeu 503), Observatório ProfEPT/EduCAPES e Google Scholar. Rodar as mesmas strings e acrescentar os registros novos em `triagem.csv`, com base = nome da base.
2. **Bola de neve (a conferir no texto completo):** itens conhecidos do pesquisador ou citados nos incluídos que as strings não captaram:
   - Black, McKinnish e Sanders (2005, *ILR Review*), boom do carvão e evasão;
   - Charles, Hurst e Notowidigdo (2018, *AER*), booms imobiliários e ensino superior;
   - Cascio e Narayan (2022, *ILR Review*), fraturamento hidráulico e escolaridade;
   - Dore e Lüscher (2011, *Cadernos de Pesquisa*), evasão no ensino técnico em MG;
   - TCU, Acórdão 506/2013-Plenário, auditoria da evasão na Rede Federal;
   - os estudos listados em `referencias.md` como "a localizar".
3. **Revisão humana da triagem:** conferir os 43 incluídos e uma amostra dos excluídos pelo título (sugestão: 50, sorteio com seed fixa) e reportar a concordância.
4. **Leitura do texto completo** dos incluídos das categorias A e B e extração de desenho, dados, escala e resultado.
