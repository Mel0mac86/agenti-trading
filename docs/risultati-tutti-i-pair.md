# Risultati backtest — tutti i pair

Generato da `scripts/run_all.py` il 2026-06-25. Dati HistData 2020–2024, costi approssimati per strumento, split OOS dal 2023, walk-forward (WF) = anni positivi su 5.

> ⚠️ Backtest bar-based approssimato → shortlist. Conferma su MT4 demo.
> La 'migliore' è la più redditizia OOS tra quelle ROBUSTE (profitto IS+OOS, DD≤25%, ≥30 trade, no artefatti).

| Pair | Migliore strategia | TF | OOS ret | PF | DD | WR | WF |
|------|--------------------|----|--------:|----:|----:|----:|:--:|
| EURUSD | RSI_rev | H1 | 13.2% | 1.20 | 5.3% | 58% | 4/5 |
| GBPUSD | MACD | D1 | 3.3% | 1.25 | 3.1% | 41% | 3/5 |
| AUDUSD | RSI_rev | H1 | 3.5% | 1.03 | 18.4% | 54% | 4/5 |
| USDCHF | Boll_rev | H1 | 20.4% | 1.10 | 11.0% | 47% | 4/5 |
| USDCAD | — | — | — | — | — | — | — |
| NZDUSD | — | — | — | — | — | — | — |
| USDJPY | EMA_cross | H4 | 18.3% | 1.94 | 5.3% | 35% | 3/5 |
| XAUUSD | EMA_cross | H1 | 51.3% | 1.47 | 14.4% | 27% | 4/5 |
| XAGUSD | Donchian | H4 | 11.2% | 1.32 | 8.8% | 34% | 3/5 |
| SPXUSD | EMA_cross | H4 | 20.2% | 2.19 | 6.2% | 23% | 3/5 |
| NSXUSD | EMA_cross | H1 | 30.4% | 1.17 | 22.8% | 26% | 5/5 |
| GRXEUR | ROC | H4 | 251.6% | 5.03 | 16.7% | 33% | 3/5 |

## Lettura critica (non fermarsi ai numeri)

**M15 escluso di proposito:** su timeframe bassi questo backtest bar-based genera
artefatti (es. forex M15 a +400% — falsi). I numeri qui sono solo H1/H4/D1.

**La colonna WF (anni positivi su 5) conta più del rendimento.** Un OOS alto con
WF basso è fragile. Ordinati per affidabilità reale:

- 🟢 **Più robusti (WF 4–5/5):** XAUUSD (oro), EURUSD, USDCHF, NSXUSD.
- 🟡 **Da verificare:** USDJPY, GBPUSD, XAGUSD, SPXUSD (WF 3/5: dipendono dal regime).
- 🔴 **Sospetto:** GRXEUR (DAX) +251% PF 5,03 — numero gonfiato da un trend fortissimo,
  WF 3/5. NON affidabile come appare; tratta come "momentum su un bull market", non edge stabile.
- ⚪ **Nessun edge robusto:** USDCAD, NZDUSD. Meglio saperlo: niente trade qui.

**Nota su NSXUSD:** WF 5/5 ottimo, ma DD 22,8% alto → ridurre il rischio.

**Nota sull'oro:** il runner indica EMA 20/100 (OOS più alto), ma il deep-dive
(`risultati-backtest-xauusd.md`) preferisce **EMA 20/50**: stesso edge ma coerenza
IS≈OOS molto migliore (44% vs 44%). La preferenza va alla coerenza, non al picco.

## Pattern confermato per asset class

| Classe | Natura dell'edge | Strumenti |
|--------|------------------|-----------|
| Metalli | **Trend-following** | XAUUSD (EMA), XAGUSD (Donchian) |
| Forex | **Mean-reversion** | EURUSD/AUDUSD (RSI), USDCHF (Bollinger) |
| Indici | **Trend/Momentum** | SPXUSD/NSXUSD (EMA), GRXEUR (ROC) |

Conferma la tesi del portafoglio: combinare trend (metalli/indici) e mean-reversion
(forex) = edge poco correlati, equity più liscia.
