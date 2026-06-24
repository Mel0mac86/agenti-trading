# Guida: avviare l'EA in demo su MetaTrader 4

Percorso per portare `FleetGuard_EA.mq4` dal codice alla demo, passo per passo.

## A. Installare e compilare l'EA

1. In MT4: **File → Apri cartella dati**. Apri `MQL4/Experts/`.
2. Copia dentro `experts/FleetGuard_EA.mq4`.
3. In MT4: **Strumenti → MetaQuotes Language Editor** (o F4). Apri l'EA e premi
   **Compila** (F7). Deve risultare *0 errori*. Comparirà in *Navigatore → Expert Advisors*.

## B. Importare i dati storici (per il backtest)

1. **Strumenti → Centro storico** (F2).
2. Seleziona il simbolo (es. XAUUSD), doppio clic sul timeframe (es. H1) → **Importa**.
3. Scegli `data/mt4/XAUUSD_H1.csv`, separatore **virgola**, conferma.
4. Ripeti per i timeframe che ti servono. (I CSV li generi con gli script del repo.)

## C. Backtest sullo Strategy Tester

1. **Visualizza → Strategy Tester** (Ctrl+R).
2. Imposta:
   - **Expert**: FleetGuard_EA
   - **Simbolo**: XAUUSD — **Periodo**: H1 (la config validata)
   - **Modello**: *Every tick* (massima qualità)
   - **Spread**: il tuo reale (XAU/USD = **8**), non "current"
   - **Date**: un intervallo ampio (es. 2020–2024)
3. **Proprietà esperto → Inputs**: imposta
   - `RiskPercent = 0.5`
   - `CommissionPerLot` = la commissione round-turn del tuo broker
   - `MaxSpreadPoints = 35` (o coerente col tuo broker)
4. **Start**. A fine test leggi il report: *Profit factor*, *Maximal drawdown*,
   *Expected payoff*. Confronta con i numeri del repo (PF ~1,3, DD per-anno 12–19%).
   Differenze sono normali: tu usi i tick del *tuo* broker.

## D. Demo live (la validazione che conta davvero)

1. Apri un **conto demo** dal tuo broker (stesse condizioni del reale che useresti).
2. Trascina FleetGuard_EA sul grafico **XAUUSD H1**.
3. Nella finestra dell'EA: scheda **Comune** → spunta *Consenti trading dal vivo*;
   scheda **Inputs** → stessi valori del backtest.
4. In alto attiva **AutoTrading** (il pulsante deve essere verde, faccina sorridente
   in alto a destra del grafico).
5. Verifica il pannello a schermo (`Comment`): mostra lo stato dei guardiani
   (DD totale, perdita giornaliera). Se scattano, l'EA smette di aprire trade.

## E. Checklist prima di pensare al reale

- [ ] Backtest con spread e commissione **reali** (non zero).
- [ ] Demo per **almeno 1–3 mesi**, su un campione di trade significativo.
- [ ] Drawdown reale entro il limite (≤10%).
- [ ] Comportamento demo coerente con il backtest (no sorprese).
- [ ] Hai accettato psicologicamente il win rate basso (~27%): tante piccole
      perdite, poche vincite grandi.

Solo dopo, eventualmente, **micro-size in reale**. L'esecuzione automatica con
denaro vero è l'ultimo passo, non il primo.

> Materiale didattico/operativo, non consulenza finanziaria. Il trading comporta
> rischio di perdita del capitale.
