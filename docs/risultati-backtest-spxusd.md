# Risultati backtest — S&P 500 (SPXUSD, 2020–2024)

Stesso processo dell'oro: dati HistData (5 anni), costi reali (spread ~0,5 punti
indice), validazione out-of-sample e walk-forward anno per anno.
Riproduci: `python3 scripts/backtest.py SPXUSD --tf M15 H1 H4 D1 --split 2023 --spread 50`

> ⚠️ Backtest bar-based approssimato → shortlist, non verità. Conferma su MT4 demo.

## Lezione n.1 — le strategie NON si trasferiscono

La **EMA 20/50** (campione sull'oro) sull'S&P **fallisce il walk-forward: 1/5 anni
positivi**. Ogni strumento richiede la propria strategia. Mai riusare a scatola
chiusa un EA da uno strumento all'altro.

## Lezione n.2 — sull'indice esiste l'edge alto-WR / basso-DD

**Bollinger reversion (D1)** — walk-forward:

| Anno | ret | PF | DD | WR |
|------|----:|----:|----:|----:|
| 2020 | −0,2% | 0,92 | 1,5% | 44% |
| 2021 | +4,4% | 4,71 | 0,8% | 71% |
| 2022 | +2,7% | 3,44 | 0,9% | 74% |
| 2023 | −0,7% | 0,75 | 2,6% | 57% |
| 2024 | +2,5% | 2,03 | 0,8% | 80% |

Win rate 70–80%, DD sempre < 3%, anni in perdita irrisori. Profilo "tranquillo".
Contropartita: **rendimenti bassi** (~2–4%/anno a rischio 0,75%). Con DD così basso
si può alzare il rischio restando prudenti. 3/5 anni positivi (i 2 negativi piatti).

## Lezione n.3 — l'opzione più redditizia ha un anno scomodo

**Donchian N55 (H4)** — walk-forward: 4/5 positivi.

| Anno | ret | PF | DD | WR |
|------|----:|----:|----:|----:|
| 2020 | +18,0% | 3,31 | 2,8% | 33% |
| 2021 | −11,8% | 0,43 | 12,8% | 14% |
| 2022 | +2,3% | 1,17 | 7,9% | 31% |
| 2023 | +0,4% | 1,05 | 5,2% | 21% |
| 2024 | +13,1% | 2,60 | 3,8% | 45% |

Anni buoni eccellenti, ma il 2021 (S&P grindy) costa −11,8%. Più rendimento, meno
serenità.

## Sintesi e scelta

| Profilo | Strategia | Pro | Contro |
|---------|-----------|-----|--------|
| Tranquillo | Bollinger rev. D1 | WR 70–80%, DD <3% | rendimento basso |
| Aggressivo | Donchian N55 H4 | anni buoni a PF 2,6–3,3 | un anno a −12% |

Su un indice, per il profilo "alto WR / basso DD" richiesto, la **Bollinger
reversion daily** è la candidata. Da validare in demo, e ideale da abbinare a un
trend system su oro: due edge poco correlati (mean-reversion su indice +
trend-following su oro) riducono il rischio complessivo di portafoglio.

Walk-forward: `python3 scripts/walkforward.py SPXUSD --strat boll20 --tf D1 --spread 50`
