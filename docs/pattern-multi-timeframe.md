# Pattern multi-timeframe (MTF)

Test del filtro multi-timeframe: tenere i segnali su H1 solo se concordi col trend
di un timeframe superiore (D1, EMA50). Mappatura D1→H1 senza look-ahead (ogni barra
H1 usa l'ultima D1 già chiusa).
Riproduci: `python3 scripts/backtest_mtf.py`

## Base vs MTF (split OOS 2023, walk-forward = anni positivi)

| Strumento | versione | DD | PF | WR | WF | OOS ret |
|-----------|----------|---:|---:|---:|:--:|--------:|
| Oro (trend) | base | 19,0% | 1,32 | 27% | 3/5 | 45,8% |
| Oro (trend) | **MTF** | **12,8%** | 1,43 | 31% | **4/5** | 37,7% |
| Nasdaq (trend) | base | 22,8% | 1,16 | 26% | 5/5 | 30,0% |
| Nasdaq (trend) | **MTF** | **16,5%** | 1,29 | 29% | 4/5 | **34,0%** |
| EUR/USD (rev) | base | 5,3% | 1,20 | 58% | **4/5** | 12,9% |
| EUR/USD (rev) | MTF | 2,6% | 1,39 | 58% | 2/5 ❌ | 9,6% |
| USD/CHF (rev) | base | 11,8% | 1,07 | 47% | 3/5 | 13,9% |
| USD/CHF (rev) | **MTF** | **4,1%** | 1,21 | 49% | 3/5 | **21,2%** |

## Il pattern

- 🟢 **TREND (oro, Nasdaq): MTF migliora in modo netto e robusto.** Allineare gli
  ingressi H1 al trend D1 elimina i contro-trend → DD molto più basso (oro −6pt,
  Nasdaq −6pt), PF e WR più alti. È sano: un trend system non deve combattere il
  trend di fondo.
- 🔴 **MEAN-REVERSION: incoerente.** USD/CHF migliora tanto (DD 12→4%), ma EUR/USD
  perde robustezza (WF 4/5 → 2/5): il filtro toglie reversion valide. La reversion
  lavora in entrambe le direzioni, gating col trend la mutila.

**Regola operativa (principiata, non cherry-picking): MTF sui trend, base sulle reversion.**

## Effetto sul portafoglio

| Portafoglio | Rendimento | maxDD | Sharpe |
|-------------|----------:|------:|-------:|
| Base | 37,1% | 7,7% | 1,20 |
| MTF (solo gambe trend) | 32,8% | 6,1% | 1,27 |

A livello di portafoglio il guadagno è modesto (Sharpe +0,07, DD −1,6pt). Il valore
vero del MTF è **ridurre il drawdown dei singoli trend**, importante per la tenuta
psicologica e il rischio di coda.

## Implementazione

`FleetGuard_EA.mq4` ha ora gli input `UseMTFTrend` / `MTF_TF` / `MTF_EMA` (default
D1, EMA50): attivo per oro e Nasdaq, da lasciare attivo sui trend. Verifica su demo.

Riproduci portafoglio MTF: `python3 scripts/portfolio.py --mtf`
