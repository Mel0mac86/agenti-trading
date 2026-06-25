# Risultati backtest — Argento (XAGUSD, 2020–2024)

Stesso processo: dati HistData (5 anni), costo realistico ~0,04 (spread argento),
validazione out-of-sample e walk-forward anno per anno.
Riproduci: `python3 scripts/backtest.py XAGUSD --tf M15 H1 H4 D1 --split 2023 --cost 0.04`

> ⚠️ Backtest bar-based approssimato → shortlist, non verità. Conferma su MT4 demo.

## Esito: l'argento conferma il tema "metalli = trend-following"

L'edge robusto sull'argento è di nuovo **trend-following**, ma con parametri
DIVERSI dall'oro (timeframe e medie più veloci) — ennesima conferma che i
parametri non si trasferiscono a scatola chiusa.

### EMA 10/30 (H4) — 4 anni su 5 positivi

| Anno | ret | PF | DD | WR | #tr |
|------|----:|----:|----:|----:|----:|
| 2020 | +6,4%  | 1,27 | 9,3%  | 24% | 72 |
| 2021 | −4,8%  | 0,83 | 16,4% | 22% | 67 |
| 2022 | +16,0% | 1,91 | 5,3%  | 38% | 47 |
| 2023 | +3,3%  | 1,14 | 9,2%  | 24% | 62 |
| 2024 | +2,0%  | 1,10 | 5,8%  | 31% | 65 |

Unico anno negativo il 2021 (−4,8%). Profilo coerente con l'oro: WR basso (~24–31%),
poche vincite grandi (vedi 2022). Da validare in demo.

### Donchian N40 (H4) — più debole (3/5)

Due anni negativi piccoli (2021, 2024): meno affidabile dell'EMA 10/30.

## Impostazione consigliata per la demo

- Strategia: EMA cross **10/30**, timeframe **H4**
- Rischio: 0,5%/trade — Stop 2×ATR(14) — uscita su incrocio opposto
- Stesso motore `FleetGuard_EA.mq4` (basta impostare FastMA=10, SlowMA=30 e girarlo su H4)

Walk-forward: `python3 scripts/walkforward.py XAGUSD --strat ema1030 --tf H4 --cost 0.04`
