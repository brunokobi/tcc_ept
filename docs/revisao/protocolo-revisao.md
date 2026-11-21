# Protocolo da revisão sistemática

- **Pergunta:** existem estudos que relacionem aderência da oferta de EPT ao território (APL) e evasão/conclusão, em escala nacional ou multicampi?
- **Bases:** Portal de Periódicos CAPES, SciELO, repositórios ProfEPT (Observatório ProfEPT/EduCAPES), BDTD, Google Scholar (complementar).
- **Strings (pt/en):** ("arranjo produtivo local" OR "APL" OR "território") AND ("evasão" OR "permanência" OR "conclusão") AND ("instituto federal" OR "educação profissional" OR "EPT"); variações com "educação a distância".
- **Período:** 2008 (Lei 11.892) – presente.
- **Critérios de inclusão/exclusão:** ver `sintese.md`, seção 2 (categorias A–D).
- **Registro:** planilha `docs/revisao/triagem.csv` (id, base, busca, título, ano, autores, fonte, DOI, incluído, categoria, etapa, motivo).
- **Execução (2026-11-21):** busca automatizada e reproduzível na OpenAlex (`scripts/search_literature.py`), triagem por LLM a revisar pelo pesquisador; CAPES, BDTD, EduCAPES e Scholar ficam para complemento manual (ver `sintese.md`, seção 5).
- **Fluxo:** PRISMA (identificação → triagem → elegibilidade → inclusão).
