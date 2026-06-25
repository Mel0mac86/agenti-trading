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

---

## Tentativo di MIGLIORARE l'M5 (filtri MTF + sessione)

Domanda onesta: si può rendere l'M5 sostenibile riducendo i trade e alzando la
qualità? Test su oro M5, costo realistico 0,20.
Riproduci: `python3 scripts/m5_improve.py`

| Config | Filtri | OOS ret | PF | #trade | WF |
|--------|--------|--------:|----:|------:|:--:|
| EMA 20/50 | nessuno | −96% | 0,87 | 4.217 | 0/5 |
| EMA 20/50 | +MTF | −81% | 0,91 | 2.817 | 0/5 |
| EMA 20/50 | +MTF+sessione | −63% | 0,91 | 1.816 | 0/5 |
| EMA 50/200 | +MTF | −38% | 1,00 | 1.727 | 1/5 |

**I filtri aiutano** (da −96% a −38%, trade da 4.200 a 1.700) ma **non bastano**:
il migliore arriva a PF 1,00 = rumore puro dopo i costi. Su M5 il movimento medio
è troppo piccolo rispetto al costo pagato su ogni trade.

### Il vero miglioramento dell'M5 è salire di timeframe

Stesso edge EMA, stessi costi:
- **M5**: −38% (migliore caso) → perde
- **H1**: +44% (validato, 4/5 anni) → guadagna

Cambia solo che su H1 il movimento copre ampiamente il costo. Non è preferenza, è
aritmetica. L'M5 non è migliorabile fino alla redditività robusta con questi costi.
