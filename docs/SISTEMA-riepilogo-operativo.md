# Sistema di trading — riepilogo operativo

Documento unico del sistema sviluppato e validato con la flotta. Tutto deriva da
dati reali HistData (2020–2024), backtest con costi reali, validazione out-of-sample
e walk-forward anno per anno.

> ⚠️ **Disclaimer.** Materiale di analisi e supporto didattico, non consulenza
> finanziaria. Il trading comporta rischio di perdita del capitale. I numeri vengono
> da backtest bar-based approssimati: la validazione che conta è la **demo** sul tuo
> broker. Nessuna garanzia di risultati futuri.

## 1. I 4 strumenti validati (i "verdi", WF 4–5/5)

| Strumento | Classe | Strategia | TF | EA | MTF |
|-----------|--------|-----------|----|----|-----|
| XAU/USD (oro) | metallo | EMA cross 20/50 | H1 | FleetGuard | ✅ D1 |
| NSXUSD (Nasdaq) | indice | EMA cross 10/30 | H1 | FleetGuard | ✅ D1 |
| EUR/USD | forex | RSI 14 (25/75) | H1 | FleetReversion (RSI) | ❌ |
| USD/CHF | forex | Bollinger 20/2.0 | H1 | FleetReversion (Boll) | opzionale |

Regola MTF: **filtro trend D1 attivo sui trend (oro, Nasdaq), spento sulle reversion**
(su EUR/USD peggiora la robustezza).

## 2. Impostazioni comuni

- **Rischio:** 0,5% per trade (margine per scalare: a 1% il portafoglio rende ~74%).
- **Stop:** 2×ATR(14) sui trend; 1,5×ATR con target 1,5×ATR (RR 1:1) sulle reversion.
- **Guardiani (in entrambi gli EA):** stop nuovi trade a −10% DD totale; stop giornaliero
  a −3%; max 2 posizioni; filtro spread; commissioni incluse nel sizing.

## 3. Il portafoglio (il vero edge)

Combinare i 4 edge (2 trend + 2 reversion, correlazioni ~0) batte ogni singola
strategia in rapporto rischio/rendimento:

| | Rendimento | maxDD | Sharpe |
|--|----------:|------:|-------:|
| Media dei 4 singoli | — | 12,1% | 0,60 |
| **Portafoglio base** | 37,1% | 7,7% | 1,20 |
| **Portafoglio MTF** | 32,8% | 6,1% | 1,27 |

Operativamente: 4 grafici H1, un EA per strumento con la sua config, **rischio uguale**.

## 4. Pattern appresi (lezioni trasversali)

1. **Le strategie non si trasferiscono** tra strumenti (EMA 20/50 vince sull'oro, fallisce sull'S&P).
2. **Per asset class:** metalli = trend, forex = mean-reversion, indici = trend/momentum.
3. **H1 è il timeframe sweet spot** (M15 = artefatti, D1 = pochi trade).
4. **Trade-off WR/DD/profitto:** sull'oro non si può avere tutto; il WR alto si trova sui forex/indici.
5. **MTF aiuta i trend** (DD oro 19→13%, Nasdaq 23→16%), **non le reversion**.
6. **Diversificare batte ottimizzare:** il salto di Sharpe viene dal portafoglio, non dai parametri.

## 5. Checklist per la demo

- [ ] Compila i due EA in MetaEditor (0 errori).
- [ ] Importa i dati (`scripts/` → History Center) o usa i dati broker.
- [ ] Backtest per ogni strumento con **spread e commissione reali** (oro = 8).
- [ ] Verifica che i numeri demo siano coerenti col backtest (no sorprese).
- [ ] Avvia i 4 EA su conto **demo**, ogni strumento sul suo TF, rischio 0,5%.
- [ ] Lascia girare **1–3 mesi**; controlla DD reale ≤ 10%.
- [ ] Hai accettato i WR bassi sui trend (~27%): tante piccole perdite, poche grandi vincite.
- [ ] Solo dopo, eventualmente, micro-size in reale.

## 6. Mappa del repository

- `experts/` — i due EA (FleetGuard trend, FleetReversion reversion).
- `scripts/` — pipeline: download, resample, backtest, backtest_v2, walkforward,
  backtest_mtf, portfolio, run_all.
- `docs/` — framework di rischio, risultati per strumento, tutti-i-pair,
  portafoglio-green, pattern-multi-timeframe, guida-demo-mt4, questo riepilogo.
- `.claude/agents/` — la flotta di subagent; `.claude/commands/` — gli slash-command.

## 7. Cosa NON fare

- Non aumentare il rischio per "recuperare" dopo una serie negativa.
- Non disattivare gli stop o allargarli.
- Non passare al reale prima della demo.
- Non fidarsi di backtest con rendimenti stratosferici (sono bug, non tesori).
- Non continuare a ottimizzare: oltre questo punto è overfitting. Tocca alla demo.
