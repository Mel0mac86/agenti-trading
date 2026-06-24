---
description: Costruisce un trade plan completo da una tesi di mercato
argument-hint: <tesi/strumento> [capitale] [rischio%]
---

Costruisci un trade plan per: **$ARGUMENTS**

Usa il subagent `planner` come capofila, coordinando `position-sizing` e
`risk-management`. Produci il piano completo:

1. **Tesi** — perché il trade, in una frase.
2. **Setup** — condizioni di ingresso e timeframe.
3. **Entry** — livello/i e logica.
4. **Stop loss** — livello e motivazione.
5. **Target** — TP1/TP2 e gestione parziali.
6. **Risk/Reward** — calcolato ed esplicito.
7. **Position size** — calcolato da `position-sizing` dato capitale e rischio%.
8. **Invalidazione** — cosa rende la tesi falsa.
9. **Scenari** — a favore / contro / laterale.

Nessun piano senza stop e rischio definiti in anticipo. Rispondi in italiano.
