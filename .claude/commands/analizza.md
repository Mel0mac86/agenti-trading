---
description: Analisi completa di uno strumento (tecnica + fondamentale + sentiment + macro)
argument-hint: <strumento> [timeframe] [orizzonte]
---

Analizza lo strumento: **$ARGUMENTS**

Usa il subagent `analyzer` come capofila. Deve delegare agli specialisti e
integrare i risultati in un unico report a livelli:

1. **Quadro tecnico** (`technical-analysis`) — trend, livelli, indicatori sui timeframe rilevanti.
2. **Quadro fondamentale** (`fundamental-analysis`) — salute dell'emittente/progetto.
3. **Sentiment** (`sentiment-analysis`) — umore e posizionamento del mercato.
4. **Macro** (`macro`) — contesto economico e di settore.
5. **Rischi noti** — cosa potrebbe invalidare il quadro.

Distingui fatti da interpretazioni, indica confidenza e fonti. Nessuna
raccomandazione operativa: questa è solo la fotografia dello stato attuale.
Rispondi in italiano.
