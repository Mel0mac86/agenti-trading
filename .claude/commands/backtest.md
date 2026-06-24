---
description: Testa e valida una strategia su dati storici, evitando overfitting
argument-hint: <strategia/regole> [strumento] [periodo]
---

Esegui il backtest della strategia: **$ARGUMENTS**

Usa il subagent `backtesting` (coordinando `optimizer` e `market-data` se serve):

1. Definisci regole, strumento, periodo e frequenza dati.
2. Includi sempre i costi: commissioni, spread, slippage, finanziamento.
3. Calcola le metriche complete: CAGR, Sharpe, Sortino, Calmar, max drawdown,
   win-rate, profit factor, expectancy.
4. Valida con walk-forward / out-of-sample, non solo in-sample.
5. Segnala bias (look-ahead, survivorship, data-snooping) e robustezza ai parametri.

Riporta una tabella metriche completa e i limiti del test. Un backtest stima un
edge, non garantisce il futuro. Rispondi in italiano.
