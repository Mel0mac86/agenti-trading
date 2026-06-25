# Money management: martingala, anti-martingala, rischio crescente

Test onesto degli schemi di gestione del rischio sulla sequenza REALE di trade
delle strategie validate. Monte Carlo (3000 rimescolamenti), capitale €100,
obiettivo €1.000.000, rovina sotto €20.
Riproduci: `python3 scripts/money_management.py XAUUSD H1 --cost 0.15`

## Risultati — Oro H1 (WR 27%, trend)

| Schema | Capitale mediano | P(rovina) | P(≥1M) |
|--------|----------------:|------:|------:|
| Fixed 2% | €439 | 0,2% | 0% |
| Fixed 5% | €298 | 34,3% | 0% |
| Martingala ×2 | €0 | 100% | 0% |
| Anti-martingala ×1,5 (cap 10%) | €274 | 0% | 0% |
| Tiered (+1%/10x, cap 8%) | €269 | 0% | 0% |

## Risultati — EUR/USD H1 (WR 58%, reversion)

| Schema | Capitale mediano | P(rovina) | P(≥1M) |
|--------|----------------:|------:|------:|
| Fixed 2% | €152 | 0% | 0% |
| Fixed 5% | €214 | 0% | 0% |
| Martingala ×2 | €138 | 37,4% | 0% |
| Anti-martingala | €136 | 0% | 0% |
| Tiered | €126 | 0% | 0% |

## Le quattro verità

1. **Martingala = rovina matematica.** WR 27% → rovina nel 100% dei casi; persino
   WR 58% → 37%. Una serie di perdite arriva sempre e il raddoppio esplode. Da non
   usare mai.
2. **Più rischio NON significa più guadagno oltre l'ottimo.** Oro da 2% a 5%: il
   mediano SCENDE (439→298) e la rovina sale al 34% (tassa della volatilità /
   over-betting oltre l'optimal-f).
3. **Anti-martingala e rischio crescente col capitale: sicuri ma non miracolosi.**
   Zero rovina, ma non battono un fixed 2% moderato. Scalare il rischio col capitale
   non accelera come si spera: la volatilità composta se lo mangia.
4. **Nessuno schema arriva a €1M** (P = 0% ovunque). Da €100, su trade reali, il
   miglior money management produce qualche centinaio di euro, non milioni.

## Conclusione operativa

- **Mai martingala.** È l'opposto della sopravvivenza del capitale.
- Il sizing giusto è **fixed fractional moderato** (≈1–2%); compounda già da solo
  (rischi di più in valore man mano che l'equity cresce).
- Aumentare la % di rischio col capitale è accettabile solo entro l'ottimo
  (oltre, peggiora rendimento e rovina). Meglio prudenti.
- Il money management ottimizza un edge esistente; **non crea** un edge né
  trasforma €100 in milioni.
