# Analisi scalping — l'edge contro il muro dei costi

Richiesta: trovare uno scalping che porti da €100 al milione. Esito (dati reali
HistData, OOS 2023–24): **lo scalping non regge ai costi reali.**

Riproduci: `python3 scripts/scalping_analysis.py`

## Oro (XAU/USD) — rendimento OOS al variare del costo/trade

| TF / Strategia | #trade | costo 0,08 | costo 0,15 | costo 0,25 | costo 0,40 |
|----------------|------:|----:|----:|----:|----:|
| M5 RSI 14 | 2.377 | −33% | −64% | −85% | −96% |
| M5 Bollinger | 10.270 | −97% | −100% | −100% | −100% |
| M15 RSI 14 | 865 | +13% | +1% | −14% | −33% |
| M15 Bollinger | 3.662 | −31% | −62% | −83% | −95% |

Ai costi reali dell'oro (spread 8 = 0,08, più commissioni e slippage ≈ 0,15–0,25)
quasi tutto è in perdita. L'unico quasi-in-pari (M15 RSI) fa +1% a costo realistico.

## EUR/USD M15 — la sensibilità che smaschera l'illusione

| Strategia | costo 0,00008 | costo 0,00015 | costo 0,00025 | costo 0,00040 |
|-----------|----:|----:|----:|----:|
| RSI 7 | +108.047% | +6.324% | +13% | −100% |
| RSI 14 | +1.901% | +375% | −39% | −97% |
| Bollinger | +158.406% | +4.157% | −76% | −100% |

**Questo è il punto chiave.** Un risultato che passa da +108.000% a −100% per un
piccolo cambio del costo **non è un edge: è rumore + costi sottostimati.** È il
backtest gonfiato tipico dei robot venduti ai principianti. Ai costi realistici
(2,5–4 pip all-in con slippage) il sistema perde tutto.

## Perché lo scalping è il modo più DIFFICILE

- Il costo (spread + commissione + slippage) si paga su OGNI trade; con migliaia
  di trade diventa il fattore dominante, spesso più grande dell'edge.
- Più basso il timeframe, più trade, più i costi schiacciano il risultato.
- Lo slippage reale (qui non pienamente modellato) peggiora ancora il quadro.

## In relazione all'obiettivo €100 → €1.000.000

- Ai costi reali lo scalping è in perdita: non avvicina al milione, lo allontana.
- A €100 il lotto minimo (0,01) dà leva ~20×: un singolo colpo di slippage può
  chiudere il conto. Le regole di money management (rischio 0,5%) sono inapplicabili.
- Anche il caso meno peggiore (oro M15, +1%) non compounda a un milione in nessun
  orizzonte ragionevole.

**Conclusione:** lo scalping non è la scorciatoia, è la via più rapida ad azzerare
i €100. La ricchezza si costruisce con capitale + tempo + sopravvivenza, non con
micro-trade ad alta frequenza su un conto minuscolo. Vedi
`obiettivo-100-a-milioni.md` per il piano realistico.
