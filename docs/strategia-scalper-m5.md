# Strategia scalper M5 pura (single TF) — analisi e verdetto

Richiesta: una strategia solo scalper, senza multi-timeframe. Ricerca completa
(sweep RSI/Bollinger/breakout su M5, filtro sessione, costi reali, walk-forward).
Riproduci: `python3 scripts/m5_scalper.py EURUSD --cost 0.00020`

## Oro M5: non scalpabile

Ogni scalper puro sull'oro M5 è in perdita ai costi reali (da −10% a −47% nei casi
con un numero di trade significativo). Confermato: l'oro non si scalpa.

## EUR/USD M5: l'unico candidato — e la sua fragilità fatale

Migliore scalper puro trovato: **EUR/USD, RSI(7) soglie 20/80, filtro sessione
(ore liquide), stop 1,5×ATR, target 1,5×ATR, M5.** Walk-forward 5/5. MA:

### Sensibilità al costo (OOS 2023–24)

| Costo all-in | OOS ret | PF | WF |
|--------------|--------:|----:|:--:|
| 1,5 pip | +15.638% | 1,44 | 5/5 |
| 2,0 pip | +467% | 1,14 | 5/5 |
| 2,5 pip | −80% | 0,89 | 2/5 |
| 3,0 pip | −99% | 0,64 | 0/5 |
| 3,5 pip | −100% | 0,51 | 0/5 |

**L'edge esiste solo con costo all-in ≤ ~2,2 pip.** PF 1,14 = margine del 14% sopra
i costi; su 4.535 trade basta mezzo pip di slippage in più per capovolgerlo in rovina.

## Verdetto

Lo scalper M5 puro è viable SOLO con:
- spread ECN ≤ ~1 pip + commissioni minime,
- slippage quasi nullo su migliaia di trade,
- esecuzione di qualità (VPS, broker serio).

Sono condizioni da conto strutturato, **non da conto retail piccolo**. Su €100, con
costi all-in reali ≥ 2,5 pip, questa strategia **perde tutto**. È il motivo
matematico per cui lo scalping retail fallisce: l'edge è più piccolo dei costi.

## Se proprio vuoi provarlo (solo demo, mai €100 reali)

- Strumento EUR/USD, timeframe M5.
- Motore: `FleetReversion_EA` in modalità RSI. Il filtro di sessione è **già incluso**.
- Preset scalper (Inputs dell'EA):
  - `SignalMode = REV_RSI`
  - `RSI_Period = 7`, `RSI_Oversold = 20`, `RSI_Overbought = 80`
  - `SL_ATR_Mult = 1.5`, `TP_ATR_Mult = 1.5`
  - `UseSessionFilter = true`, `StartHour = 3`, `EndHour = 12` (adatta al fuso del tuo broker)
  - `RiskPercent = 0.5`, `CommissionPerLot` = quella reale del tuo broker
- **Prima di tutto: misura il TUO costo all-in reale.** Se è > 2 pip, non ha senso partire.

Vedi anche `analisi-scalping.md` (costi) e `obiettivo-100-a-milioni.md` per il quadro completo.
