# Grid trading (griglia): l'analisi onesta

Richiesta: lo scalping a griglia. Test su dati reali (5 anni) di una griglia long
classica: livelli ogni G, take-profit +G per livello, NESSUNO stop.
Riproduci: `python3 scripts/grid_backtest.py XAUUSD H1 --grid 5`

## Risultati (lotto minimo, 1 unità)

| Metrica | Oro H1 (passo $5) | EUR/USD H1 (passo 30 pip) |
|---------|------------------:|--------------------------:|
| Profitto realizzato | +1.025 | +6,3 |
| Max drawdown FLOTTANTE | −363 | −4,6 |
| Max posizioni aperte insieme | 13 | 55 |
| Profitto / rischio-picco | 2,82 | 1,37 |

## Le quattro verità sulla griglia

1. **Incassa a gocce, rischia tutto insieme.** Su EUR/USD ha accumulato 55 posizioni
   aperte in perdita durante la discesa, senza stop. Il rischio non è per trade: è
   l'intero conto in un colpo se il mercato non torna indietro.
2. **Il caso oro "buono" è fortuna di direzione.** La griglia long ha reso perché
   l'oro è salito 5 anni. In un mercato che scende accumula perdite all'infinito.
   È una scommessa direzionale travestita da sistema neutro; i +1.025 sull'oro li
   facevi anche comprando e tenendo.
3. **Incompatibile con €100.** Il DD flottante dell'oro (−363 in prezzo) col lotto
   minimo (0,01 = 1 oz) vale −$363: azzera un conto da €100 più volte. Servono
   migliaia di euro di cuscinetto solo per il lotto minimo.
4. **Nessun edge.** La griglia non prevede nulla: gestisce esposizione. Aggiunge
   rischio di coda ILLIMITATO (niente stop) senza vantaggio statistico.

## Verdetto

Come martingala e scalping ad alta frequenza, la griglia è il profilo
"vince-spesso / perde-tutto": tanti piccoli guadagni che mascherano una perdita
catastrofica latente. Viola la regola n.1 (sopravvivenza del capitale). Da evitare,
specie su conto piccolo. Vedi anche `money-management.md` e `analisi-scalping.md`.
