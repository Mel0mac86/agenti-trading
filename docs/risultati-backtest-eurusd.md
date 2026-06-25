# Risultati backtest — EUR/USD (2020–2024)

Stesso processo: dati HistData (5 anni), costo realistico ~1,5 pip, validazione
out-of-sample e walk-forward anno per anno.
Riproduci: `python3 scripts/backtest.py EURUSD --tf M15 H1 H4 D1 --split 2023 --cost 0.00015`

> ⚠️ Backtest bar-based approssimato → shortlist, non verità. Conferma su MT4 demo.

## ⚠️ Lezione fondamentale: gli artefatti del M15

Il backtest ha prodotto su M15 numeri assurdi (RSI reversion: **+6324% OOS, +12851%
in-sample**). **Sono FALSI e vanno scartati.** Perché:

- Migliaia di micro-trade (3000–4500) compoundati gonfiano un micro-edge in numeri
  di fantasia.
- Su timeframe bassi il modello bar-based riempie le entrate di reversion a prezzi
  troppo ideali; in reale **spread + slippage su ogni trade** azzerano l'edge.

Regola: se un backtest mostra rendimenti stratosferici, **non è un tesoro, è un bug**.
La validazione si fa su timeframe più alti e, soprattutto, in demo.

## L'edge vero: il forex è mean-reversion

A differenza dei metalli (trend), EUR/USD premia la **mean-reversion**. Versione
realistica e robusta su **H1**.

### RSI reversion 14 (25/75), H1 — 4 anni su 5 positivi

| Anno | ret | PF | DD | WR | #tr |
|------|----:|----:|----:|----:|----:|
| 2020 | +2,0%  | 1,06 | 6,4%  | 60% | 139 |
| 2021 | +8,5%  | 1,32 | 4,9%  | 59% | 122 |
| 2022 | −4,8%  | 0,86 | 12,1% | 53% | 130 |
| 2023 | +2,9%  | 1,12 | 3,6%  | 55% | 113 |
| 2024 | +10,6% | 1,29 | 5,3%  | 60% | 149 |

Win rate stabile 53–60%, DD basso. L'unico anno negativo è il 2022, quando il
dollaro ha avuto un trend fortissimo (la mean-reversion soffre nei trend forti):
comportamento atteso e coerente, non un difetto.

## Impostazione consigliata per la demo

- Strategia: **RSI(14) reversion**, soglie 25/75, timeframe **H1**
- Ingresso: long sotto 25, short sopra 75 — Stop/Target 1,5×ATR (RR 1:1)
- Rischio: 0,5%/trade
- Codice: il motore di `FleetReversion_EA.mq4` (oggi Bollinger) può ospitare l'RSI
  sostituendo la funzione `Signal()`.

Walk-forward: `python3 scripts/walkforward.py EURUSD --strat rsi2575 --tf H1 --cost 0.00015`
