# Framework di rischio e protocollo di backtest (MT4)

Obiettivo del progetto: sviluppare con la flotta strategie EA per MT4 su **oro, indici,
metalli e forex** che siano profittevoli **al netto di spread, commissioni e drawdown**.

> ⚠️ Nessuno può garantire profitti né "conto mai in rosso". Le perdite fanno parte del
> trading. Qui si lavora perché i **costi siano una frazione piccola dell'edge** e il
> **drawdown sia limitato per costruzione**. Tutto va validato in demo prima del reale.

## 1. Profilo di rischio raccomandato (fase demo)

| Parametro | Valore | Perché |
|-----------|--------|--------|
| Rischio per trade | **0,75%** dell'equity | Sopravvivenza prima del rendimento |
| Drawdown totale (soft-stop) | **−10%** → stop nuovi trade | Evita la spirale delle perdite |
| Perdita giornaliera (stop) | **−3%** → stop per la giornata | Blocca le giornate-no |
| Posizioni contemporanee | **2** per EA | Limita il rischio aggregato |
| R:R minimo | **1,5** | L'edge deve coprire ampiamente i costi |
| Correlazione | evita oro + argento + indici insieme | In stress le correlazioni vanno a 1 |

Questi valori sono i default di `FleetGuard_EA.mq4` e sono modificabili dagli `input`.

## 2. Costi: la regola d'oro

Lo spread e le commissioni vanno **sempre** inclusi nel backtest. Regola pratica:

> Il **costo medio per trade** (spread + commissione) deve essere **≤ 1/3 del guadagno
> medio atteso per trade**. Se non lo è, la strategia non è robusta: o si allargano i
> target (timeframe più alto), o si scarta.

Per questo l'EA include `CommissionPerLot` nel calcolo del lotto e filtra lo spread
(`MaxSpreadPoints`): se lo spread è troppo alto, **non entra**.

## 3. Protocollo di backtest sullo Strategy Tester di MT4

1. **Dati**: usa "Every tick" (massima qualità). Verifica il *modeling quality* ~90%.
   Per oro/indici/metalli procurati dati storici di buona qualità (history center / broker).
2. **Costi reali**: imposta lo **spread** del tuo broker (non "current"/zero) e inserisci
   la **commissione** in `CommissionPerLot`. Senza questo il test mente.
3. **Periodo**: almeno 3–5 anni, includendo fasi diverse (trend, range, alta volatilità).
4. **In-sample / Out-of-sample**: ottimizza su una parte (es. 2021–2023), poi **verifica
   senza ritoccare nulla** su un periodo mai visto (es. 2024–2026). Se crolla → overfitting.
5. **Walk-forward**: ripeti il ciclo ottimizza→verifica su finestre scorrevoli.
6. **Per strumento**: oro, indici, metalli e forex hanno volatilità e costi diversi.
   Testa e taratura **separati per simbolo**; non dare per scontato che un set valga per tutti.

## 4. Metriche da accettare/rifiutare

Una strategia è candidabile alla demo solo se, **out-of-sample e con costi reali**:
- **Profit factor** ≥ 1,3
- **Max drawdown** entro il limite del profilo (≤10%)
- **Expectancy** positiva e stabile tra i simboli
- Numero di trade **statisticamente significativo** (≥ ~100), non 10 colpi fortunati
- Curva equity senza dipendere da pochi trade enormi

Se anche **una** di queste salta → si torna all'`optimizer`, non si va in reale.

## 5. Come collabora la flotta su questo obiettivo

1. `strategist` → sceglie regime e quali strumenti/stili affrontare per primi.
2. `technical-analysis` + `macro` → definiscono l'idea di edge (es. trend-following su oro).
3. `mql4-developer` → la traduce in codice EA dentro `FleetGuard_EA.mq4`.
4. `backtesting` + `optimizer` → definiscono il protocollo e leggono i risultati che **tu**
   produci sullo Strategy Tester (MT4 gira sul tuo PC, non qui).
5. `risk-management` + `position-sizing` → fissano i parametri salva-conto.
6. `advisor` → revisione finale prima di passare alla demo.
7. `journaling` → registra gli esiti della demo e alimenta il ciclo di miglioramento.

## 6. Percorso operativo (niente scorciatoie)

```
Idea → codice EA → backtest con costi reali → out-of-sample → walk-forward
     → (se supera le metriche) → DEMO almeno 1-3 mesi → revisione advisor
     → solo allora, eventualmente, micro-size in reale
```

L'esecuzione automatica in reale è l'**ultimo** passo, non il primo.
