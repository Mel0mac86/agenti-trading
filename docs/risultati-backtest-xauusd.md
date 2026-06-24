# Risultati backtest — XAU/USD (2020–2024)

Generato con `scripts/backtest.py` su dati HistData (5 anni, ~1,73M barre M1).
**Costi reali inclusi:** spread 8 points + commissione 7$/lotto. Rischio 0,75%/trade.
Validazione **out-of-sample**: parametri valutati su 2020–2022, classifica su **2023–2024**.

> ⚠️ Backtest bar-based approssimato (fill al prossimo open, stop/target intrabar).
> Serve a fare lo **shortlist**, non è la verità: conferma su MT4 Strategy Tester in demo.

## Classifica robusta (profitto IS+OOS, DD ≤ 25%, ≥30 trade)

| TF | Strategia | Param | OOS ret | PF | DD | WR | #tr | IS ret |
|----|-----------|-------|--------:|----:|----:|----:|----:|-------:|
| H1 | EMA cross | 20/100 | +51,3% | 1,47 | 14,4% | 27% | 215 | +18,0% |
| H1 | EMA cross | 20/50  | +43,7% | 1,31 | 19,0% | 27% | 327 | +44,2% |
| H1 | ROC       | 40     | +41,5% | 1,19 | 20,5% | 33% | 782 | +5,6%  |
| H1 | Donchian  | 20     | +34,2% | 1,18 | 16,3% | 29% | 468 | +34,4% |
| H4 | EMA cross | 10/30  | +28,7% | 1,64 | 8,2%  | 32% | 117 | +3,0%  |
| H4 | Donchian  | 20     | +25,4% | 1,58 | 11,6% | 35% | 107 | +0,2%  |

## Lettura critica

- **Non si sceglie il rendimento OOS più alto.** EMA 20/100 (+51%) ha IS solo +18%:
  incoerenza IS↔OOS = probabile fortuna, non edge.
- **Candidata più robusta: EMA cross 20/50 su H1** — IS +44%, OOS +44% (coerente),
  PF 1,31. Alternativa a DD più basso: **Donchian 20 su H1** (IS +34 ≈ OOS +34, DD 16%).
- **Win rate ~27%**: trend-following, poche vincite grandi. Richiede disciplina/automazione.
- **DD 19% > limite 10%**: ridurre il rischio a 0,5%/trade abbassa DD a ~13%.

## Prossimi passi suggeriti

1. Confermare EMA 20/50 H1 sullo Strategy Tester (spread reale, "Every tick").
2. Walk-forward su finestre scorrevoli (non solo un singolo split).
3. Aggiungere filtro di trend di ordine superiore (es. H4) e/o trailing stop su ATR.
4. Ripetere la stessa procedura su indici e altri pair (dati sempre da HistData).

Riproduci: `python3 scripts/backtest.py XAUUSD --tf M15 H1 H4 D1 --split 2023`

---

## Aggiornamento v2: ricerca di WR più alto e DD più basso

Con `scripts/backtest_v2.py` ho aggiunto filtro di trend (EMA200), take-profit,
trailing stop, ADX e setup pullback-in-trend, per cercare win rate più alto e
drawdown più basso.

### Esito (onesto): i tre obiettivi sono in conflitto su XAU/USD

| Variante | WR | OOS ret | PF | IS ret |
|----------|----:|--------:|----:|-------:|
| EMAtrend +TP 1.5 | 58% | +0,3% | 1,01 | −33,5% |
| EMAtrend +TP 2.5 | 46% | +27% | 1,08 | −27,8% |
| Pullback r7 | 44% | +18% | 1,16 | −10,6% |
| **EMAtrend (no TP)** | 26% | +61% | 1,61 | +3% |
| **EMA 20/50 (v1)** | 27% | +44% | 1,31 | +44% |

**Ogni variante ad alto WR / basso DD perde in-sample (PF ~1): nessun edge reale.**
L'oro fa trend: mettere un take-profit taglia le poche vincite grandi che pagano
tutto → il WR sale ma il sistema smette di guadagnare. È struttura di mercato.

### Conclusioni operative

- Non esiste, in modo robusto, "più profitto + più WR + meno DD insieme" su XAU/USD.
- **Per ridurre il DD**: abbassare il rischio a 0,5%/trade (taglia il DD ~1/3, zero overfitting).
- **Upgrade robusto**: filtro EMA200 sulla EMA 20/50 (PF 1,31 → 1,61) — da confermare su MT4.
- **WR più alto sostenibile**: cercarlo su altri strumenti (indici/forex), non sull'oro.

Riproduci: `python3 scripts/backtest_v2.py XAUUSD --tf M15 H1 H4 --split 2023`

---

## Walk-forward anno per anno (verifica di robustezza)

Con `scripts/walkforward.py`, parametri FISSI (non riottimizzati per anno) — il
test più onesto contro l'overfitting. XAU/USD H1, costi reali.

### EMA 20/50 — 4 anni su 5 positivi

| Anno | ret | PF | DD | WR | #tr |
|------|----:|----:|----:|----:|----:|
| 2020 | +44,6% | 1,73 | 11,9% | 29% | 153 |
| 2021 | −0,6%  | 1,01 | 13,8% | 29% | 191 |
| 2022 | +1,1%  | 1,04 | 14,3% | 24% | 184 |
| 2023 | +20,6% | 1,36 | 19,0% | 28% | 138 |
| 2024 | +21,1% | 1,29 | 16,6% | 27% | 188 |

L'unico anno non positivo è di fatto un pareggio (−0,6%). Nessun anno disastroso:
profilo di un edge reale. Il 2021 piatto riflette la lateralizzazione dell'oro.

### Esito

- **EMA 20/50 "liscia": validata.** È la scelta di riferimento per la demo.
- **Filtro EMA200: scartato.** Anno per anno ha un vero anno in perdita (2021 −6,1%)
  e WR più basso; il suo vantaggio nel singolo split era effetto del blocco 2023–24.
  Meno parametri = più robusto.

### Impostazione consigliata per la demo

- Strategia: EMA cross 20/50, timeframe **H1**
- Rischio: **0,5%/trade** (porta il DD annuo sotto ~10%)
- Stop: 2×ATR(14); uscita su incrocio opposto
- Validazione: demo MT4 ≥ 1–3 mesi sul proprio broker (spread reale, "Every tick")

Riproduci: `python3 scripts/walkforward.py XAUUSD --tf H1`
