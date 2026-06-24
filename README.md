# agenti-trading

Una **flotta di subagent per Claude Code** dedicata al trading, ispirata allo schema
ad albero degli assistenti finanziari ma riadattata ai mercati: analisi, pianificazione,
ottimizzazione, consulenza di rischio e strategia.

Gli agenti vivono in [`.claude/agents/`](.claude/agents/): Claude Code li invoca
automaticamente in base alla descrizione, oppure puoi richiamarli per nome.

## Gerarchia

```
                          Claude Code
                               │
   ┌───────────┬──────────────┼──────────────┬───────────────┐
 analyzer    planner       optimizer        advisor        strategist
(Analista) (Pianificatore) (Ottimizzatore) (Consulente)    (Stratega)
                               │
   ┌──────────────┬───────────┼────────────┬──────────────┐
 technical-    fundamental- sentiment-   risk-          position-
 analysis      analysis     analysis     management     sizing
   │              │            │            │              │
 portfolio    backtesting  order-       market-data     crypto
                            execution
   │              │            │            │              │
 forex         options       macro        taxes        journaling
```

## Agenti principali (livello strategico)

| Agente | Ruolo | Quando usarlo |
|--------|-------|---------------|
| **analyzer** | Analista di mercato | Fotografare lo stato di uno strumento (tecnica + fondamentale + sentiment + macro) |
| **planner** | Pianificatore di trade | Trasformare una tesi in un trade plan completo (entry, stop, target, size) |
| **optimizer** | Ottimizzatore di strategia | Migliorare strategie/portafoglio via backtest e tuning, evitando overfitting |
| **advisor** | Consulente di rischio | Second opinion, controllo disciplina e bias prima di agire |
| **strategist** | Stratega | Visione d'insieme: stile, allocazione, regime di mercato, orchestrazione |

## Specialisti (livello operativo)

| Agente | Dominio |
|--------|---------|
| **technical-analysis** | Trend, livelli, pattern, indicatori, price action |
| **fundamental-analysis** | Bilanci, multipli, tokenomics, salute dell'emittente |
| **sentiment-analysis** | Fear & Greed, funding, posizionamento, narrativa |
| **risk-management** | Money management, drawdown, esposizione, R/R |
| **position-sizing** | Dimensionamento posizioni (il "budget" del rischio) |
| **portfolio** | Allocazione, diversificazione, correlazione, ribilanciamento |
| **backtesting** | Test storici, metriche, walk-forward, anti-overfitting |
| **order-execution** | Tipi di ordine, slippage, spread, esecuzione |
| **market-data** | Reperimento, validazione e qualità dei dati |
| **crypto** | Asset digitali, on-chain, DeFi, rischi di custodia |
| **forex** | Coppie valutarie, pip/lotti, sessioni, carry |
| **options** | Greche, volatilità, payoff, strategie in opzioni |
| **macro** | Cicli, banche centrali, tassi, calendario eventi |
| **taxes** | Fiscalità e reportistica del trading (focus Italia) |
| **journaling** | Trading journal, statistiche, psicologia e disciplina |

## Flusso tipico

1. **strategist** definisce il quadro (regime, stile, allocazione).
2. **analyzer** valuta lo strumento delegando agli specialisti di analisi.
3. **planner** costruisce il trade plan con `position-sizing` e `risk-management`.
4. **advisor** fa da controllo qualità su rischio e bias.
5. **order-execution** traduce il piano in ordini concreti.
6. **journaling** registra l'esito; **optimizer** affina nel tempo.

## ⚠️ Avvertenza

Questi agenti sono strumenti di **analisi e supporto didattico**. Non costituiscono
consulenza finanziaria, fiscale o di investimento personalizzata. Il trading comporta
il rischio di perdita del capitale. Verifica sempre i dati e la normativa aggiornata e,
quando serve, rivolgiti a professionisti abilitati.
