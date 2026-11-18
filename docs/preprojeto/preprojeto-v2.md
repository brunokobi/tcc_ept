# Pré-projeto de TCC — EaD na EPT (IFSul) · versão 2

> Revisão de 18/11/2026 da [versão 1](preprojeto.md) (PDF original ao lado). Mudanças principais em relação à v1: mecanismos concorrentes no lugar de uma hipótese unidirecional; dois mapeamentos independentes entre atividade econômica e curso (texto com IA e mercado de trabalho via CBO); desenho de identificação *shift-share*; escopo dividido em núcleo e extensões; referencial em texto corrido; operacionalização das variáveis. Os números de viabilidade vêm de [prospeccao/relatorio-viabilidade.md](../prospeccao/relatorio-viabilidade.md).

## Título e resumo

**Título provisório:** Aderência territorial, permanência e conclusão na educação profissional técnica da Rede Federal: evidência nacional para cursos presenciais e a distância com inteligência artificial e dados abertos

A Lei 11.892/2008 manda os Institutos Federais orientarem a oferta para os arranjos produtivos locais, mas não se sabe se cursos alinhados ao território retêm mais ou menos estudantes. A teoria aponta em duas direções. Um curso ligado à economia local dá sentido à formação e perspectiva de inserção, o que favorece a permanência. Um mercado de trabalho aquecido no próprio setor do curso, porém, aumenta o custo de oportunidade de continuar estudando e pode puxar o estudante para o emprego antes da conclusão. A pesquisa mede qual mecanismo predomina, em que tipo de curso e em qual modalidade.

A estrutura produtiva de cada território vem da RAIS e da base de CNPJ; a oferta e os desfechos vêm dos microdados da Plataforma Nilo Peçanha (PNP); o Catálogo Nacional de Cursos Técnicos (CNCT) liga atividade econômica e curso por dois caminhos independentes: um classificador com IA (embeddings e LLM) sobre os textos da CNAE e do CNCT, e uma ponte empírica pelas ocupações da CBO que o próprio CNCT associa a cada curso. A identificação combina painel com efeitos fixos e um instrumento *shift-share*. Hipóteses, variáveis e modelos são pré-registrados no OSF. A pesquisa usa apenas dados públicos e agregados.

**Palavras-chave:** educação profissional e tecnológica; educação a distância; evasão; arranjos produtivos locais; mercado de trabalho local; inteligência artificial.

## Contextualização e justificativa

A territorialidade é parte da identidade legal da Rede Federal. A Lei 11.892/2008 (art. 6º, IV) atribui aos Institutos Federais a tarefa de orientar sua oferta "em benefício da consolidação e fortalecimento dos arranjos produtivos, sociais e culturais locais", e as Diretrizes Curriculares Nacionais Gerais da EPT (Resolução CNE/CP 1/2021) reforçam o vínculo entre itinerários formativos e o mundo do trabalho. A literatura sobre a expansão da Rede (PACHECO, 2011) defende essa diretriz como instrumento de desenvolvimento regional, mas a evidência empírica disponível é de estudos de caso de um campus por vez. Não há medida padronizada de aderência nem teste, em escala nacional, de sua relação com os resultados acadêmicos.

A evasão é o problema concreto que dá urgência à questão. Os indicadores da PNP mostram taxas de evasão elevadas nos cursos técnicos, e mais altas nos cursos a distância. Estudos nacionais com dados da PNP descrevem a evasão e a associam a características do estudante e do curso, mas não à estrutura econômica do lugar onde o curso é ofertado.

A pergunta não tem resposta óbvia. Se a aderência aumentar a permanência, a diretriz legal ganha respaldo empírico e a gestão ganha um critério para planejar a oferta. Se o efeito for o contrário — mercados fortes no setor do curso puxando estudantes para o trabalho antes da conclusão —, a resposta adequada é outra: certificação intermediária, flexibilização de horários, oferta subsequente ou EaD para trabalhadores. Nos dois casos, o resultado orienta política pública.

A pesquisa se justifica por quatro contribuições:

- **Empírica:** primeira medida nacional de aderência territorial da oferta técnica da Rede Federal e primeiro teste de sua relação com evasão e conclusão.
- **Teórica:** confronta dois mecanismos com previsões opostas e identifica as condições (tipo de curso, modalidade, faixa etária) em que cada um predomina.
- **Metodológica:** um mapeamento CNAE → CNCT construído por IA e validado contra anotação humana e contra uma ponte independente pelo mercado de trabalho (CBO), publicado como dado aberto.
- **Para a EaD:** mostra se o vínculo territorial da oferta a distância — cujo estudante pode estar longe do campus — se comporta como o da oferta presencial.

## Problema e pergunta de pesquisa

**Problema:** a aderência territorial da oferta técnica é uma diretriz legal sem medida sistemática nem evidência nacional sobre sua relação com permanência e conclusão; a direção esperada dessa relação também é teoricamente ambígua.

**Pergunta:** a aderência entre os cursos técnicos da Rede Federal e a estrutura produtiva do seu território está associada à evasão e à conclusão? Em que direção, por qual mecanismo, e essa associação difere entre EaD e presencial?

**Hipóteses** (pré-registradas, com direção):

- **H1a — pertencimento e perspectiva:** maior aderência estrutural (o peso do setor do curso na economia do território) está associada a menor evasão e maior conclusão.
- **H1b — custo de oportunidade:** choques positivos de demanda por trabalho no setor do curso, durante o ciclo, estão associados a maior evasão, mais fortes nos cursos subsequentes e entre estudantes mais velhos.
- **H2 — modalidade:** a associação da aderência estrutural com evasão é mais fraca na EaD, cujo estudante está menos ligado ao território do campus.

H1a e H1b não são excludentes: o desenho separa o **nível** da aderência (estrutura do território) da **variação** de curto prazo da demanda (choque), e cada um corresponde a um mecanismo.

## Objetivos

**Objetivo geral:** analisar, em escala nacional, a relação entre a aderência territorial dos cursos técnicos da Rede Federal e seus indicadores de evasão e conclusão, distinguindo os mecanismos de pertencimento e de custo de oportunidade e comparando EaD e presencial.

**Objetivos específicos:**

1. Construir um mapeamento CNAE → CNCT com IA e validá-lo contra anotação humana (dois avaliadores) e contra uma ponte independente pelas ocupações CBO.
2. Caracterizar a estrutura produtiva de cada território da Rede Federal com dados de emprego formal (RAIS) e estabelecimentos (CNPJ).
3. Propor e calcular índices de aderência estrutural e de choque de demanda por curso, território e ano.
4. Estimar a associação entre aderência, evasão e conclusão, testando H1a, H1b e H2.
5. Publicar dados, código e mapeamento em repositório aberto com DOI.

## Referencial teórico

**EPT, território e a crítica ao ajuste ao mercado.** A expansão da Rede Federal foi justificada pela interiorização e pelo desenvolvimento local (PACHECO, 2011). Ao mesmo tempo, a tradição crítica da EPT brasileira (FRIGOTTO; CIAVATTA; RAMOS, 2005) recusa a formação subordinada às demandas imediatas do mercado e defende o trabalho como princípio educativo. A pesquisa adota uma noção de aderência que não é ajuste da escola ao empregador, mas vínculo do curso com o território onde o estudante vive e trabalha, e trata essa tensão como objeto: se a aderência aumentar a evasão por custo de oportunidade, o resultado reforça a crítica de que o mercado compete com a escola pelo estudante trabalhador.

**Evasão e permanência.** O modelo de integração de Tinto (1975) explica a evasão pela integração acadêmica e social do estudante à instituição. Para estudantes não tradicionais — mais velhos, que trabalham, que estudam a distância —, Bean e Metzner (1985) mostram que fatores do ambiente externo, entre eles as oportunidades de emprego, pesam mais que a integração social. Kember (1989) e Rovai (2003) estendem esses modelos à educação a distância, em que as condições externas e as responsabilidades de trabalho e família são centrais. No Brasil, Dore e Lüscher (2011) descrevem a evasão na educação técnica de nível médio como processo associado à trajetória escolar e à inserção no trabalho. A aderência territorial entra nesses modelos como variável de ambiente: positiva, quando dá sentido ao percurso (integração acadêmica, perspectiva de carreira); negativa, quando o emprego no setor compete com a escola.

**Mercado de trabalho local e decisão de estudar.** A economia da educação documenta que a demanda local por trabalho afeta a permanência escolar. O *boom* do carvão nos Estados Unidos reduziu a matrícula de jovens (BLACK; MCKINNISH; SANDERS, 2005); a expansão do *fracking* aumentou o abandono do ensino médio entre homens (CASCIO; NARAYAN, 2022); a chegada de empregos industriais de exportação no México elevou o abandono escolar (ATKIN, 2016). Esses estudos sustentam H1b e oferecem o desenho *shift-share* usado aqui (BARTIK, 1991; GOLDSMITH-PINKHAM; SORKIN; SWIFT, 2020; BORUSYAK; HULL; JARAVEL, 2022).

**EaD na EPT.** A teoria da distância transacional (MOORE; KEARSLEY, 2013) e a análise de Belloni (2009) situam a EaD como modalidade que amplia o alcance territorial, mas enfraquece o vínculo com a instituição. Daí H2: se o estudante de EaD está menos ligado ao território do campus, a aderência medida nesse território deve explicar menos sua permanência.

**IA para classificação e dados educacionais.** Revisões sobre IA na educação (ZAWACKI-RICHTER et al., 2019) apontam o predomínio de aplicações preditivas e a escassez de uso da IA para construir medidas. Embeddings de sentença (REIMERS; GUREVYCH, 2019) e LLMs como anotadores (GILARDI; ALIZADEH; KUBLI, 2023; ZIEMS et al., 2024) tornam viável classificar textos administrativos em escala, desde que validados contra anotação humana e com concordância medida (KRIPPENDORFF, 2004).

## Trabalhos correlatos

| Linha | O que existe | Lacuna coberta |
|---|---|---|
| Aderência da oferta aos APLs | Estudos de caso por campus: IFC Camboriú (CARVALHO; ZOTTI; BRANDT, 2025), IFRJ, IFMA, IFSC, IFMG, IFAP | Escala nacional, medida padronizada, relação com desempenho |
| Evasão com dados da PNP | Análises descritivas nacionais; regressão por campus; aprendizado de máquina multicampi | Estrutura produtiva do território como fator explicativo |
| Evasão na EaD técnica | Predição com dados de AVA (TAMADA, 2022) | Fatores territoriais e estruturais, em toda a Rede |
| Mercado de trabalho local e escolarização | *Booms* setoriais e abandono escolar (BLACK; MCKINNISH; SANDERS, 2005; ATKIN, 2016; CASCIO; NARAYAN, 2022) | Educação profissional, Brasil, aderência curso–setor |

A revisão sistemática (protocolo PRISMA em `docs/revisao/`) deve confirmar a ausência de estudo nacional sobre aderência e evasão na Rede Federal.

## Metodologia

Pesquisa aplicada, quantitativa e explicativa, com dados secundários públicos e escopo nacional.

### Fontes de dados

| Fonte | Conteúdo | Papel |
|---|---|---|
| PNP — microdados de matrícula e eficiência acadêmica | Uma linha por matrícula: curso, tipo, modalidade, eixo, ciclo, situação, município da unidade | Oferta e desfechos |
| RAIS (microdados públicos de vínculos, PDET) | Vínculos por município, subclasse CNAE e ocupação CBO, por ano | Estrutura produtiva, choques de demanda, ponte CBO |
| Base de CNPJ (Receita Federal) | Estabelecimentos por CNAE, porte, município, abertura e baixa | Robustez (estabelecimentos) e eventos |
| CNCT 4ª ed. (atualizada em 29/11/2024) | 214 cursos em 13 eixos, perfil, campo de atuação, ocupações CBO associadas, permissão de EaD | Ponte curso ↔ atividade |
| CNAE 2.3 (IBGE) | 1.332 subclasses com notas explicativas | Texto para o classificador |
| Divisão regional do IBGE (2017) | Regiões geográficas imediatas e intermediárias | Território |

### Operacionalização das variáveis

| Variável | Definição | Fonte |
|---|---|---|
| Evasão do ciclo | Matrículas evadidas ÷ matrículas do ciclo, ao fim do prazo previsto | PNP (eficiência) |
| Conclusão do ciclo | Concluintes ÷ matrículas do ciclo | PNP (eficiência) |
| Aderência estrutural (Q) | Quociente locacional do emprego ligado ao curso no território, no ano de início do ciclo | RAIS + mapeamento |
| Choque de demanda (S) | Variação do emprego ligado ao curso no território durante o ciclo | RAIS + mapeamento |
| Instrumento *shift-share* (B) | Composição setorial inicial do território × crescimento nacional de cada setor, excluído o território | RAIS |
| EaD | Modalidade da oferta | PNP |
| Controles | Eixo, tipo de curso, turno, carga horária, vagas, idade da oferta, perfil agregado dos ingressantes (faixa etária, renda, cor/raça), população e PIB per capita do território | PNP, IBGE |

### Etapas

**Núcleo** (necessário para o artigo principal):

1. **Painel de dados:** ciclos de matrícula × ano, com desfechos agregados por oferta (curso × unidade × modalidade × tipo) e a estrutura produtiva anual de cada território.
2. **Mapeamento CNAE → curso por dois caminhos:**
   - **Texto com IA:** embeddings das descrições e notas da CNAE e dos perfis e campos de atuação do CNCT, similaridade e LLM para casos ambíguos, com justificativa registrada.
   - **Mercado de trabalho (CBO):** peso de cada subclasse em cada curso = participação, nos vínculos da subclasse, das ocupações CBO que o CNCT associa ao curso.
3. **Validação:** amostra estratificada de cerca de 300 subclasses anotada por dois avaliadores (o pesquisador e um segundo avaliador), com concordância entre e intra-avaliador; precisão, revocação e F1 por eixo; comparação com linha de base por palavras-chave; concordância entre LLMs; e convergência entre os dois caminhos.
4. **Índices:** aderência estrutural (quociente locacional) e choque de demanda, por curso, território e ano.
5. **Pré-registro no OSF** antes de qualquer estimação de efeito.
6. **Modelos principais:** regressão para proporções (logit fracionário ponderado por matrículas), erros agrupados por território. Como a aderência estrutural quase não muda no tempo (ver prospecção), H1a e H2 são estimadas com efeitos fixos de campus × ciclo e de curso × ciclo: o mesmo curso é comparado entre campi, e cada campus é comparado consigo mesmo entre cursos. H1b usa a variação do choque de demanda dentro da mesma oferta, com efeitos fixos de oferta e de ano.
7. **Identificação:** instrumento *shift-share* para o choque de demanda; placebos de território e de eixo; robustez a definição de território, mapeamento e edição do CNCT.

**Extensões** (fazer se o núcleo fechar no prazo):

8. Estudo de evento com aberturas e fechamentos de grandes estabelecimentos (base de CNPJ), com estimador para adoção escalonada (CALLAWAY; SANT'ANNA, 2021).
9. Modelo de aprendizado de máquina com SHAP para comparar a importância relativa da aderência.
10. Painel web e servidor MCP para consulta dos resultados.

### Estratégia de identificação

| Análise | Pergunta | O que resolve |
|---|---|---|
| Efeitos fixos de campus × ciclo e curso × ciclo (H1a, H2) | O mesmo curso evade menos nos campi onde seu setor é mais forte, comparado aos outros cursos do mesmo campus? | Tudo o que é do campus/território e tudo o que é do curso no país |
| Efeitos fixos de oferta e ano (H1b) | Quando a demanda no setor do curso cresce durante o ciclo, a evasão daquela oferta muda? | Diferenças fixas entre ofertas e choques nacionais |
| Instrumento *shift-share* | O crescimento nacional dos setores ligados ao curso, ponderado pela composição inicial do território, prevê a evasão? | Endogeneidade da demanda local (ex.: o campus afeta a economia local) |
| Placebo de território | A aderência a um território sorteado e distante prevê evasão? | Não deveria; se prever, o modelo capta outro fator |
| Placebo de eixo | A aderência a um eixo sem relação com o curso prevê evasão? | Mesmo objetivo |
| Seleção da oferta | Ofertas abertas em territórios de alta aderência diferem antes de abrir? | Discute a abertura não aleatória de cursos |
| Robustez | Outra definição de território, mapeamento (texto × CBO), edição do CNCT e ponderação | O achado não depende de uma escolha específica |
| Heterogeneidade | Tipo de curso (integrado, concomitante, subsequente), modalidade, eixo, faixa etária dos ingressantes | Separa H1a de H1b e aprofunda H2 |

**Poder estatístico:** antes do pré-registro, uma simulação com a estrutura real do painel (número de ofertas, ciclos por oferta e variância intra-oferta da aderência) estima o menor efeito detectável, e esse número é reportado junto aos resultados.

### Pré-registro e ciência aberta

Hipóteses com direção, variáveis, modelos, testes e regras de exclusão serão registrados no OSF antes da estimação; desvios serão documentados. Dados derivados, código e o mapeamento CNAE → CNCT serão publicados com DOI no Zenodo. Os resultados serão reportados como vierem, inclusive nulos ou contrários às hipóteses.

**Ferramentas:** Python (pandas, DuckDB, statsmodels, linearmodels, scikit-learn, sentence-transformers), LLMs via API (dois provedores) e o pipeline de dados da Receita Federal já desenvolvido pelo pesquisador.

## Aspectos éticos e limitações

A pesquisa usa apenas dados públicos, anonimizados na origem e analisados de forma agregada, sem participação de pessoas, e se enquadra na dispensa de apreciação pelo sistema CEP/Conep (Resolução CNS 510/2016, art. 1º, parágrafo único, incisos II e III). Nenhum dado pessoal é tratado: os microdados da PNP são agregados por oferta e ciclo antes da análise.

**Limitações:**

- **Associação e causalidade:** efeitos fixos e o instrumento *shift-share* reduzem, mas não eliminam, vieses de dados observacionais.
- **Território do estudante de EaD:** os microdados da PNP localizam a unidade de ensino, não a residência do estudante. A aderência da EaD é medida no território da unidade, e H2 é interpretada como diferença no vínculo com esse território.
- **Emprego formal:** a RAIS não cobre informalidade nem MEI; setores com muita informalidade terão aderência subestimada.
- **Atividade principal:** a CNAE principal esconde atividades secundárias.
- **Série histórica da PNP:** mudanças de metodologia (como a reestruturação de 2024) exigem harmonização documentada.
- **Seleção da oferta:** cursos não são abertos ao acaso; a análise de seleção e os efeitos fixos tratam parte disso.
- **Sobreposição com o mestrado:** o TCC não reutiliza o experimento de redes neurais de grafos; usa a base de CNPJ com pergunta e método próprios.

## Resultados esperados e produtos

- Evidência nacional sobre aderência, evasão e conclusão, com os mecanismos separados e comparação entre EaD e presencial.
- Mapeamento CNAE → CNCT validado, publicado como dado aberto com suas métricas.
- Artigo principal no formato do curso, preparado para periódico A1 da área de Educação (ex.: *Ensaio: Avaliação e Políticas Públicas em Educação*, *Cadernos de Pesquisa*, *Educação & Sociedade*, *Revista Brasileira de Educação*).
- Segundo artigo sobre o mapeamento com IA para a área de Informática na Educação.
- Extensão: painel web e servidor MCP para consulta pública.

## Cronograma

Meses relativos ao início do TCC; ajustar ao calendário oficial. O núcleo vem antes das extensões.

| Etapa | Meses | Tipo |
|---|---|---|
| Revisão sistemática e refinamento com o orientador | 1–2 | núcleo |
| Coleta e harmonização (PNP, RAIS, CNCT, CNAE, IBGE) | 1–3 | núcleo |
| Anotação de referência (dois avaliadores) e reanotação | 2–4 | núcleo |
| Mapeamentos (texto com IA e CBO) e validação | 3–4 | núcleo |
| Simulação de poder e pré-registro no OSF | 4 | núcleo |
| Índices, modelos principais e identificação | 4–6 | núcleo |
| Redação do artigo e revisão | 6–8 | núcleo |
| Estudo de evento, SHAP, painel e MCP | 6–8 | extensão |
| Entrega e defesa | 9 | — |

## Referências

ATKIN, D. Endogenous skill acquisition and export manufacturing in Mexico. *American Economic Review*, v. 106, n. 8, p. 2046-2085, 2016.

BARTIK, T. J. *Who benefits from state and local economic development policies?* Kalamazoo: W. E. Upjohn Institute, 1991.

BEAN, J. P.; METZNER, B. S. A conceptual model of nontraditional undergraduate student attrition. *Review of Educational Research*, v. 55, n. 4, p. 485-540, 1985.

BELLONI, M. L. *Educação a distância*. 5. ed. Campinas: Autores Associados, 2009.

BLACK, D. A.; MCKINNISH, T. G.; SANDERS, S. G. Tight labor markets and the demand for education: evidence from the coal boom and bust. *ILR Review*, v. 59, n. 1, p. 3-16, 2005.

BORUSYAK, K.; HULL, P.; JARAVEL, X. Quasi-experimental shift-share research designs. *The Review of Economic Studies*, v. 89, n. 1, p. 181-213, 2022.

BRASIL. Lei nº 11.892, de 29 de dezembro de 2008. Institui a Rede Federal de Educação Profissional, Científica e Tecnológica, cria os Institutos Federais de Educação, Ciência e Tecnologia, e dá outras providências. *Diário Oficial da União*, Brasília, 30 dez. 2008.

BRASIL. Conselho Nacional de Educação. Resolução CNE/CP nº 1, de 5 de janeiro de 2021. Define as Diretrizes Curriculares Nacionais Gerais para a Educação Profissional e Tecnológica. *Diário Oficial da União*, Brasília, 6 jan. 2021.

BRASIL. Conselho Nacional de Educação. Câmara de Educação Básica. Resolução CNE/CEB nº 2, de 15 de dezembro de 2020. Aprova a quarta edição do Catálogo Nacional de Cursos Técnicos. *Diário Oficial da União*, Brasília, 16 dez. 2020.

BRASIL. Ministério da Educação. *Catálogo Nacional de Cursos Técnicos*. 4. ed. Brasília: MEC, 2020 (conteúdo alterado em 29 nov. 2024).

BRASIL. Conselho Nacional de Saúde. Resolução nº 510, de 7 de abril de 2016. *Diário Oficial da União*, Brasília, 24 maio 2016.

CALLAWAY, B.; SANT'ANNA, P. H. C. Difference-in-differences with multiple time periods. *Journal of Econometrics*, v. 225, n. 2, p. 200-230, 2021.

CARVALHO, M. T.; ZOTTI, S. A.; BRANDT, A. G. A relação dos arranjos produtivos locais e os cursos técnicos integrados: o caso do Instituto Federal Catarinense – Campus Camboriú. *Revista Brasileira da Educação Profissional e Tecnológica*, v. 1, n. 25, e16800, 2025. DOI: 10.15628/rbept.2025.16800.

CASCIO, E. U.; NARAYAN, A. Who needs a fracking education? The educational response to low-skill-biased technological change. *ILR Review*, v. 75, n. 1, p. 56-89, 2022.

DORE, R.; LÜSCHER, A. Z. Permanência e evasão na educação técnica de nível médio em Minas Gerais. *Cadernos de Pesquisa*, v. 41, n. 144, p. 770-789, 2011.

FRIGOTTO, G.; CIAVATTA, M.; RAMOS, M. (org.). *Ensino médio integrado: concepção e contradições*. São Paulo: Cortez, 2005.

GILARDI, F.; ALIZADEH, M.; KUBLI, M. ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences*, v. 120, n. 30, e2305016120, 2023.

GOLDSMITH-PINKHAM, P.; SORKIN, I.; SWIFT, H. Bartik instruments: what, when, why, and how. *American Economic Review*, v. 110, n. 8, p. 2586-2624, 2020.

KEMBER, D. A longitudinal-process model of drop-out from distance education. *The Journal of Higher Education*, v. 60, n. 3, p. 278-301, 1989.

KRIPPENDORFF, K. *Content analysis: an introduction to its methodology*. 2. ed. Thousand Oaks: Sage, 2004.

MOORE, M. G.; KEARSLEY, G. *Educação a distância: sistemas de aprendizagem on-line*. 3. ed. São Paulo: Cengage Learning, 2013.

NOSEK, B. A. et al. The preregistration revolution. *Proceedings of the National Academy of Sciences*, v. 115, n. 11, p. 2600-2606, 2018.

PACHECO, E. (org.). *Institutos Federais: uma revolução na educação profissional e tecnológica*. Brasília: Fundação Santillana; São Paulo: Moderna, 2011.

REIMERS, N.; GUREVYCH, I. Sentence-BERT: sentence embeddings using Siamese BERT-networks. In: CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING (EMNLP-IJCNLP), 2019, Hong Kong. *Proceedings* [...]. ACL, 2019. p. 3982-3992.

ROVAI, A. P. In search of higher persistence rates in distance education online programs. *The Internet and Higher Education*, v. 6, n. 1, p. 1-16, 2003.

TAMADA, M. M. *Predição de evasão de cursos técnicos em EaD através de técnicas de aprendizado de máquina em duas etapas*. 2022. Tese (Doutorado em Informática) – Universidade Federal do Amazonas, Manaus, 2022.

TINTO, V. Dropout from higher education: a theoretical synthesis of recent research. *Review of Educational Research*, v. 45, n. 1, p. 89-125, 1975.

ZAWACKI-RICHTER, O. et al. Systematic review of research on artificial intelligence applications in higher education – where are the educators? *International Journal of Educational Technology in Higher Education*, v. 16, art. 39, 2019.

ZIEMS, C. et al. Can large language models transform computational social science? *Computational Linguistics*, v. 50, n. 1, p. 237-291, 2024.

**A localizar e completar durante a revisão:** estudos do IFRJ (Eng. Paulo de Frontin), IFMA, IFSC (Itajaí), IFMG, IFAP (Santana), IFTO (Araguaína), Ifes (Barra de São Francisco), ENIAC 2024 (aprendizado de máquina com a PNP) e as análises nacionais da revista do ProfEPT (2025).
