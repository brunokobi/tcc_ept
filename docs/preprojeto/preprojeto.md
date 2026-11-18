# Pré-projeto de TCC — EaD na EPT (IFSul)

> Transcrição do PDF `preprojeto-tcc-ead-ept-ifsul.pdf` (18/11/2026). O PDF é o registro original; as specs detalham a implementação.

## Título e resumo

**Título provisório:** Aderência territorial e desempenho da educação a distância na Rede Federal de EPT: evidência nacional com inteligência artificial e dados abertos

A pesquisa testa se cursos técnicos alinhados à estrutura produtiva do seu território têm menor evasão e maior conclusão, e se esse efeito é diferente na EaD e no presencial. A estrutura produtiva vem da base nacional de CNPJ da Receita Federal; a oferta e os indicadores acadêmicos vêm da Plataforma Nilo Peçanha; o Catálogo Nacional de Cursos Técnicos (CNCT) faz a ponte entre atividade econômica e curso.

Um classificador com IA (embeddings semânticos e LLM) associa subclasses CNAE a eixos e cursos do CNCT, com validação documentada. Um índice de aderência por curso e território é relacionado aos indicadores acadêmicos por regressão multinível. A pesquisa usa apenas dados públicos, sem participação de pessoas.

**Palavras-chave:** educação a distância; educação profissional e tecnológica; arranjos produtivos locais; evasão; inteligência artificial; dados abertos.

## Contextualização e justificativa

A Lei 11.892/2008 determina que os Institutos Federais orientem sua oferta formativa para fortalecer os arranjos produtivos, sociais e culturais locais. Essa diretriz é central na identidade da Rede Federal, mas quase não há evidência empírica, em escala nacional, de que a aderência ao território se traduz em melhores resultados acadêmicos.

A questão é ainda mais aberta na EaD. Um curso a distância pode atender alunos longe do campus, o que tanto pode ampliar a aderência a demandas locais quanto descolar a oferta do território. Ao mesmo tempo, a evasão na EaD técnica é historicamente alta, e entender seus fatores estruturais é prioridade para a gestão.

A pesquisa se justifica por quatro motivos:

- **Lacuna de evidência:** testa empiricamente, em toda a Rede Federal, uma diretriz legal que costuma ser tratada só no plano conceitual.
- **Relevância para a EaD na EPT:** indica se, e onde, alinhar a oferta a distância ao território reduz evasão.
- **Contribuição metodológica:** propõe um mapeamento CNAE → CNCT com IA, validado e publicado como dado aberto, reutilizável por outros pesquisadores e gestores.
- **Viabilidade:** usa apenas dados públicos e um pipeline de dados da Receita Federal já desenvolvido pelo pesquisador.

## Problema e pergunta de pesquisa

**Problema:** a aderência territorial da oferta de EPT é uma diretriz legal, mas não existe medida sistemática dela nem evidência nacional sobre sua relação com evasão e conclusão, especialmente na EaD.

**Pergunta de pesquisa:** a aderência entre os cursos técnicos da Rede Federal e a estrutura produtiva do seu território está associada a menor evasão e maior conclusão, e essa associação difere entre EaD e presencial?

**Hipóteses:**

- **H1:** cursos com maior aderência territorial apresentam menor evasão e maior conclusão, controlando eixo, campus, ano e perfil da oferta.
- **H2:** a associação entre aderência e desempenho tem intensidade diferente na EaD e no presencial.

## Objetivos

**Objetivo geral:** analisar, em escala nacional, a relação entre a aderência territorial dos cursos técnicos da Rede Federal e seus indicadores de evasão e conclusão, comparando EaD e presencial.

**Objetivos específicos:**

1. Construir e validar um classificador com IA que associe subclasses CNAE a eixos e cursos do CNCT.
2. Caracterizar a estrutura produtiva de cada território da Rede Federal a partir da base nacional de CNPJ, ponderada por empregos (RAIS).
3. Propor e calcular um índice de aderência por curso e território.
4. Estimar a associação entre aderência, evasão e conclusão, com comparação entre modalidades.
5. Publicar dados, código e um painel interativo para consulta e replicação dos resultados.

## Referencial teórico

| Eixo | Questão central | Autores e marcos de partida |
|---|---|---|
| EPT e território | O papel dos IFs no desenvolvimento local e a relação entre formação e trabalho | Pacheco; Frigotto, Ciavatta e Ramos; Lei 11.892/2008; Resolução CNE/CP 1/2021 |
| EaD na EPT | Alcance territorial, limites e condições da oferta a distância de cursos técnicos | Moore e Kearsley; Belloni; CNCT (4ª edição) |
| Evasão escolar | Fatores institucionais e de contexto associados à permanência | Tinto (1975); estudos com dados da Plataforma Nilo Peçanha |
| IA e dados educacionais | Uso de modelos de linguagem e dados abertos para apoiar decisões educacionais | Zawacki-Richter et al. (2019); Reimers e Gurevych (2019) |

A revisão inicial deve confirmar se já existem estudos que relacionem aderência territorial e evasão na Rede Federal (busca no Portal de Periódicos CAPES, SciELO e repositórios do ProfEPT).

**Posicionamento teórico:** parte importante da literatura brasileira de EPT, como Frigotto, Ciavatta e Ramos, critica a subordinação da formação às demandas do mercado. A pesquisa não trata a aderência como ajuste da escola ao mercado, mas como vínculo do curso com o território onde o estudante vive: condição para desenvolvimento local, para a permanência e para o sentido do percurso formativo. Essa tensão será discutida explicitamente na análise dos resultados.

## Trabalhos correlatos

Uma busca inicial (a ser ampliada em revisão sistemática) mostra que cada parte do tema já foi estudada, mas não foi encontrado trabalho que relacione aderência territorial e evasão em escala nacional.

| Linha | O que existe | O que falta e esta pesquisa cobre |
|---|---|---|
| Aderência da oferta aos APLs | Estudos de caso por campus: IFC Camboriú (Carvalho, Zotti e Brandt, RBEPT, 2025), IFRJ Engenheiro Paulo de Frontin, IFMA (dissertação com plataforma de mapeamento de APLs), IFSC Itajaí, IFMG, IFAP Santana | Escala nacional, medida padronizada e relação com desempenho acadêmico |
| Evasão com dados da PNP | Análises nacionais descritivas (revista do ProfEPT, 2025); regressão por campus (IFTO Araguaína); ML multicampi com microdados da PNP (ENIAC, 2024) | Estrutura produtiva do território como fator explicativo |
| Evasão na EaD técnica | Predição com aprendizado de máquina a partir de dados do AVA (Tamada, tese UFAM, 2022) | Fatores estruturais e territoriais, em toda a Rede Federal |

**Indício a favor da hipótese:** um estudo recente sobre o Ifes Campus Barra de São Francisco apontou, de forma qualitativa, o descompasso entre a oferta e o arranjo produtivo local entre os fatores de evasão e ociosidade de vagas. Esta pesquisa testa essa relação quantitativamente e em escala nacional.

**Pontos de atenção para a metodologia:**

- **Edição do CNCT:** a 5ª edição do Catálogo passou por consulta pública em 2026, com revisão de 197 cursos em 13 eixos. É preciso definir qual edição o classificador usa, ou prever compatibilidade entre as duas.
- **Ponte por ocupações (a verificar):** se o CNCT associa ocupações da CBO a cada curso, a RAIS por CBO e município pode complementar ou validar o classificador CNAE → CNCT.

## Metodologia

Pesquisa aplicada, quantitativa e explicativa, com dados secundários de acesso público e escopo nacional (toda a Rede Federal de EPT).

### Fontes de dados

| Fonte | O que fornece | Papel na pesquisa |
|---|---|---|
| Base de CNPJ da Receita Federal | Empresas ativas de todo o país com CNAE, porte e município | Estrutura produtiva do território |
| RAIS agregada (PDET) | Vínculos de emprego por CNAE e município | Ponderar a demanda por empregos |
| Plataforma Nilo Peçanha | Cursos, modalidade, vagas, matrículas e indicadores por ciclo (evasão, conclusão, eficiência acadêmica) | Oferta e variáveis de desfecho |
| Catálogo Nacional de Cursos Técnicos | Eixos, cursos, perfis profissionais e campos de atuação | Ponte entre CNAE e curso |
| Divisão regional do IBGE | Regiões geográficas imediatas e intermediárias | Definição do território de cada oferta |

### Etapas

1. **Preparação dos dados:** montar um painel curso × ano com os indicadores por ciclo de matrícula e a estrutura produtiva de cada território ano a ano (RAIS anual e base de CNPJ).
2. **Amostra de referência:** anotar manualmente uma amostra estratificada de cerca de 300 subclasses CNAE em eixos do CNCT; reanotar 20% após quatro semanas para medir a consistência (concordância intra-avaliador).
3. **Classificador com IA:** gerar embeddings das descrições CNAE e dos campos de atuação do CNCT, associar por similaridade e usar LLMs para os casos ambíguos, com justificativa registrada.
4. **Avaliação do classificador:** precisão, revocação e F1 por eixo contra a amostra de referência; concordância entre LLMs diferentes (alfa de Krippendorff); comparação com uma linha de base por palavras-chave.
5. **Índice de aderência:** para cada curso e ano, medir o peso do seu eixo na estrutura produtiva do território (participação nos empregos).
6. **Pré-registro:** registrar hipóteses, variáveis, modelos e testes no OSF antes de estimar qualquer efeito.
7. **Modelagem principal:** regressão multinível (cursos aninhados em campi e territórios) e modelo de painel com efeitos fixos, com interação aderência × modalidade para testar H2.
8. **Estratégia de identificação:** estudo de evento, testes placebo, robustez e heterogeneidade.
9. **Interpretação complementar:** modelo de ML com explicabilidade (SHAP) para comparar a importância da aderência com os demais fatores.
10. **Publicação:** dados, código e painel interativo para replicação.

### Estratégia de identificação

Como a pesquisa usa dados observacionais, a associação entre aderência e evasão pode refletir outros fatores. As análises abaixo testam se o resultado se sustenta:

| Análise | Pergunta | O que resolve |
|---|---|---|
| Painel com efeitos fixos de curso e ano | Quando a aderência de um mesmo curso muda ao longo do tempo, a evasão muda junto? | Elimina diferenças fixas entre cursos e campi e choques nacionais de cada ano |
| Estudo de evento | Abertura ou fechamento de grandes empregadores de um setor altera a evasão dos cursos daquele eixo no território? | Verifica tendências anteriores ao choque e a dinâmica do efeito |
| Placebo de território | A aderência a um território sorteado e distante também prevê evasão? | Não deveria; se prever, o modelo capta outro fator |
| Placebo de eixo | A aderência a um eixo sem relação com o curso prevê evasão? | Mesmo objetivo do placebo de território |
| Robustez | O resultado se mantém com outras definições de território, de ponderação e com outra edição do CNCT? | Mostra que o achado não depende de uma escolha específica |
| Heterogeneidade | O efeito varia por eixo, tipo de curso (integrado, subsequente) e modalidade? | Aprofunda H2 e indica onde a aderência importa mais |

### Pré-registro e ciência aberta

As hipóteses, as variáveis, os modelos e os testes acima serão registrados no OSF antes da estimação, e qualquer desvio do plano será documentado. Dados derivados, código e o mapeamento CNAE → CNCT serão publicados com DOI no Zenodo. Os resultados serão reportados como vierem, inclusive se as hipóteses não se confirmarem.

**Ferramentas:** Python (pandas, statsmodels, scikit-learn, sentence-transformers), LLMs via API e o pipeline de dados da Receita Federal já existente do pesquisador.

## Aspectos éticos e limitações

A pesquisa usa apenas dados públicos e agregados, sem participação de pessoas, e por isso se enquadra na dispensa de apreciação pelo sistema CEP/Conep prevista na Resolução CNS 510/2016 (pesquisa com informações de acesso público). Nenhum dado pessoal é usado: a análise trabalha com contagens por CNAE, território e curso.

**Limitações previstas:**

- **Associação não é causalidade:** a estratégia de identificação reduz, mas não elimina, esse limite.
- **Território do aluno EaD:** o aluno pode morar longe do campus ou polo de oferta. Verificar o nível de localização disponível na PNP.
- **Emprego formal apenas:** a RAIS não cobre informalidade nem MEI.
- **CNAE principal esconde atividades secundárias:** o mapeamento pode subestimar alguns eixos.
- **Mudanças nos dados ao longo dos anos:** ajustes de metodologia da PNP exigem harmonizar a série histórica.
- **Sobreposição com outras pesquisas do autor:** o TCC não reutiliza o experimento de redes neurais de grafos do mestrado; usa a base de CNPJ com pergunta e método próprios.

## Resultados esperados e produtos

**Resultados científicos:**

- Evidência nacional sobre a relação entre aderência territorial, evasão e conclusão, com comparação entre EaD e presencial.
- Um mapeamento CNAE → CNCT validado e publicado como dado aberto, com suas métricas.
- Um artigo científico no formato exigido pelo curso (base para periódico de Educação) e um segundo artigo sobre o classificador (Informática na Educação).

**Produto técnico: painel interativo**

- **Painel web** com mapa de aderência por território, filtros por eixo, modalidade e ano, e os indicadores de evasão e conclusão.
- **Servidor MCP** que expõe as consultas do painel como ferramentas, para uso por clientes de IA.
- **Chat no painel** com um LLM que responde perguntas em linguagem natural usando apenas as ferramentas do MCP, sempre mostrando a consulta e os números de origem.

O chat é avaliado sem participação de pessoas: cerca de 100 perguntas com respostas conferidas por consulta direta aos dados, medindo a taxa de respostas corretas e de respostas sem base nos dados.

## Cronograma

Ver [../cronograma.md](../cronograma.md).

## Referências iniciais

Ver [../revisao/referencias.md](../revisao/referencias.md).
