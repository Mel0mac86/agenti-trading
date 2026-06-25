# Miglioramento via portafoglio — i 4 strumenti "verdi"

Dai pattern letti sui 4 strumenti più robusti (WF 4–5/5) emerge l'improvement che
funziona davvero: **combinarli**, non ottimizzare i parametri (overfitting).

Riproduci: `python3 scripts/portfolio.py`

## Pattern individuati

1. **Tutti su H1** — timeframe "sweet spot" (sopra il rumore M15, sotto la lentezza D1).
2. **Due regimi opposti:** trend (oro, Nasdaq) + mean-reversion (EUR/USD, USD/CHF).
3. **Profili complementari:** i trend hanno WR basso/DD alto, le reversion WR alto/DD basso.

## Risultato del portafoglio equal-risk (0,5%/trade, 2020–2024)

| Strumento | Rendimento | maxDD | Sharpe |
|-----------|----------:|------:|-------:|
| XAUUSD (oro, trend) | +72,2% | 14,8% | 0,76 |
| EURUSD (rev) | +12,5% | 7,3% | 0,52 |
| USDCHF (rev) | +12,3% | 15,9% | 0,37 |
| NSXUSD (Nasdaq, trend) | +49,3% | 10,3% | 0,76 |
| **PORTAFOGLIO** | **+37,1%** | **7,7%** | **1,20** |

- Sharpe portafoglio **1,20** vs media singoli 0,60 (raddoppiato) e vs miglior singolo 0,76.
- maxDD **7,7%** vs media singoli 12,1%: più basso di quasi tutti i componenti.

## Matrice di correlazione (rendimenti mensili)

|        | XAU | EUR | CHF | NSX |
|--------|----:|----:|----:|----:|
| XAUUSD | 1,00 | 0,07 | −0,01 | −0,10 |
| EURUSD | 0,07 | 1,00 | 0,12 | 0,01 |
| USDCHF | −0,01 | 0,12 | 1,00 | 0,18 |
| NSXUSD | −0,10 | 0,01 | 0,18 | 1,00 |

Correlazioni ~0: gli edge sono indipendenti → la diversificazione è reale.

## Implicazione operativa

- Tradare **tutti e 4** a rischio uguale (0,5%) batte qualsiasi singola strategia
  in rapporto rischio/rendimento.
- Il DD basso (7,7%) lascia margine: a 1%/trade il portafoglio rende ~74% (come
  l'oro da solo) ma con percorso molto più liscio (Sharpe 1,2 vs 0,76).
- In pratica: 4 grafici H1, ogni strumento col suo EA/impostazione validata
  (vedi `guida-demo-mt4.md`), rischio uguale per strumento.

> ⚠️ Backtest bar-based approssimato. La diversificazione è robusta (correlazioni
> basse confermate), ma i numeri assoluti vanno verificati in demo sul proprio broker.
