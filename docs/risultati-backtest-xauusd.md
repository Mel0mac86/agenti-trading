# Risultati backtest — XAU/USD (2020–2024)

Generato con `scripts/backtest.py` su dati HistData (5 anni, ~1,73M barre M1).
**Costi reali inclusi:** spread 8 points + commissione 7$/lotto. Rischio 0,75%/trade.
Validazione **out-of-sample**: parametri valutati su 2020–2022, classifica su **2023–2024**.

> ⚠️ Backtest bar-based approssimato (fill al prossimo open, stop/target intrabar).
> Serve a fare lo **shortlist**, non è la verità: conferma su MT4 Strategy Tester in demo.

## Classifica robusta (profitto IS+OOS, DD ≤ 25%, ≥30 trade)

| TF | Strategia | Param | OOS ret | PF | DD | WR | #tr | IS ret |
|----|-----------|-------|--------:|----:|----:|----:|----:|-------:|
| H1 | EMA cross | 20/100 | +51,3% | 1,47 | 14,4% | 27% | 215 | +18,0% |
| H1 | EMA cross | 20/50  | +43,7% | 1,31 | 19,0% | 27% | 327 | +44,2% |
| H1 | ROC       | 40     | +41,5% | 1,19 | 20,5% | 33% | 782 | +5,6%  |
| H1 | Donchian  | 20     | +34,2% | 1,18 | 16,3% | 29% | 468 | +34,4% |
| H4 | EMA cross | 10/30  | +28,7% | 1,64 | 8,2%  | 32% | 117 | +3,0%  |
| H4 | Donchian  | 20     | +25,4% | 1,58 | 11,6% | 35% | 107 | +0,2%  |

## Lettura critica

- **Non si sceglie il rendimento OOS più alto.** EMA 20/100 (+51%) ha IS solo +18%:
  incoerenza IS↔OOS = probabile fortuna, non edge.
- **Candidata più robusta: EMA cross 20/50 su H1** — IS +44%, OOS +44% (coerente),
  PF 1,31. Alternativa a DD più basso: **Donchian 20 su H1** (IS +34 ≈ OOS +34, DD 16%).
- **Win rate ~27%**: trend-following, poche vincite grandi. Richiede disciplina/automazione.
- **DD 19% > limite 10%**: ridurre il rischio a 0,5%/trade abbassa DD a ~13%.

## Prossimi passi suggeriti

1. Confermare EMA 20/50 H1 sullo Strategy Tester (spread reale, "Every tick").
2. Walk-forward su finestre scorrevoli (non solo un singolo split).
3. Aggiungere filtro di trend di ordine superiore (es. H4) e/o trailing stop su ATR.
4. Ripetere la stessa procedura su indici e altri pair (dati sempre da HistData).

Riproduci: `python3 scripts/backtest.py XAUUSD --tf M15 H1 H4 D1 --split 2023`
