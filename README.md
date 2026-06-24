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

## Progetto MT4 (Expert Advisor)

Filone dedicato allo sviluppo di EA per MetaTrader 4 su **oro, indici, metalli e forex**,
con priorità a contenere **spread, commissioni e drawdown**.

- [`experts/FleetGuard_EA.mq4`](experts/FleetGuard_EA.mq4) — motore EA *risk-first* e
  *cost-aware*: sizing su rischio %, soft-stop su DD totale, stop giornaliero, filtri
  spread/sessione, commissioni incluse nel rischio. La strategia è agganciabile nella
  funzione `Signal()`.
- [`docs/framework-rischio-e-backtest.md`](docs/framework-rischio-e-backtest.md) — profilo
  di rischio raccomandato, regola dei costi e protocollo di backtest sullo Strategy Tester.
- Specialista dedicato: **mql4-developer**.

> Il backtest gira su MT4 (sul tuo PC): la flotta scrive il codice, definisce il protocollo
> e legge i risultati. Esecuzione in reale solo come ultimo passo, dopo demo e revisione.

## Slash-command

Comandi pronti in [`.claude/commands/`](.claude/commands/) per orchestrare gli agenti:

| Comando | Cosa fa |
|---------|---------|
| `/analizza <strumento>` | Analisi completa (tecnica + fondamentale + sentiment + macro) |
| `/trade-plan <tesi>` | Costruisce un trade plan completo (entry, stop, target, size) |
| `/risk-check <trade>` | Second opinion su rischio, disciplina e bias |
| `/backtest <strategia>` | Testa e valida una strategia su dati storici |
| `/journal <trade>` | Registra un trade e analizza statistiche ed errori |

Le regole comuni a tutta la flotta sono in [`CLAUDE.md`](CLAUDE.md).

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
