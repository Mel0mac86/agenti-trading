#!/usr/bin/env python3
"""
m5_improve.py - Si puo' rendere l'M5 sostenibile ai costi reali?

L'M5 classico muore sui costi (vedi analisi-scalping.md). Qui si prova a MIGLIORARLO
riducendo i trade e alzando la qualita':
  - filtro multi-timeframe: opera M5 solo nel verso del trend H1 (EMA50);
  - filtro di sessione: solo ore liquide (London/NY), spread piu' stretti;
  - trend con target ampi invece di reversion stretta.

Costo realistico oro M5 = 0.20 (spread 0.08 + commissione + slippage).
Dati HistData in EST. Validazione OOS + walk-forward.

Uso: python3 m5_improve.py
"""
import os, datetime
from backtest import (load, atr, ema, run, sig_ema_cross, sig_rsi_rev,
                      ATR_PERIOD, DATADIR)

PAIR = "XAUUSD"
COST = 0.20
SPLIT = 2023
# finestra liquida in EST: ~03:00 (apertura Londra) - 11:30 (overlap NY)
SESS_START, SESS_END = 3, 12


def h1_trend_on_m5(m5_t):
    """Trend H1 (EMA50) mappato sulle barre M5, senza look-ahead."""
    t, o, h, l, c = load(os.path.join(DATADIR, f"{PAIR}_H1.csv"))
    e = ema(c, 50)
    tr = [0]*len(c)
    for i in range(len(c)):
        if e[i] is not None:
            tr[i] = 1 if c[i] > e[i] else -1
    dur = datetime.timedelta(minutes=60); out = [0]*len(m5_t); j = -1
    for i, tt in enumerate(m5_t):
        while j+1 < len(t) and t[j+1] + dur <= tt:
            j += 1
        if j >= 0: out[i] = tr[j]
    return out


def apply_filters(sig, times, hi, use_mtf, use_sess):
    g = list(sig)
    for i in range(len(g)):
        if g[i] == 0: continue
        if use_mtf and not ((g[i] > 0 and hi[i] > 0) or (g[i] < 0 and hi[i] < 0)):
            g[i] = 0; continue
        if use_sess and not (SESS_START <= times[i].hour < SESS_END):
            g[i] = 0
    return g


def yrs_pos(bars, a, sig, mode, ks, kt):
    t = bars[0]; w = tot = 0
    for y in sorted({d.year for d in t}):
        idx = [i for i, d in enumerate(t) if d.year == y]
        if not idx: continue
        s, e = idx[0], idx[-1]+1
        r = run(tuple(x[s:e] for x in bars), sig[s:e], mode, a[s:e], ks, kt, COST)
        if r: tot += 1; w += 1 if r["ret"] > 0 else 0
    return f"{w}/{tot}"


def main():
    p = os.path.join(DATADIR, f"{PAIR}_M5.csv")
    if not os.path.exists(p):
        print(f"manca {PAIR}_M5.csv"); return
    t, o, h, l, c = load(p); a = atr(h, l, c, ATR_PERIOD)
    bars = (t, o, h, l, c)
    hi = h1_trend_on_m5(t)
    si = next((i for i, d in enumerate(t) if d.year >= SPLIT), len(t))

    # configurazioni: trend EMA con stop/target ampi (poche vincite grandi)
    configs = [
        ("EMA20/50 trend",       lambda: sig_ema_cross(o,h,l,c,20,50), 2.0, 0.0),
        ("EMA20/50 trend TPwide", lambda: sig_ema_cross(o,h,l,c,20,50), 2.0, 4.0),
        ("EMA50/200 trend",      lambda: sig_ema_cross(o,h,l,c,50,200), 2.0, 0.0),
    ]
    print(f"# {PAIR} M5 — si puo' migliorare? costo {COST} | OOS da {SPLIT}\n")
    hdr = f'{"config":22}{"filtri":14}{"OOSret":>8}{"PF":>6}{"DD":>7}{"WR":>5}{"#tr":>6}{"WF":>6}'
    print(hdr); print("-"*len(hdr))
    for name, fn, ks, kt in configs:
        base, mode = fn()
        for label, mtf, sess in [("nessuno",0,0), ("MTF",1,0), ("MTF+sess",1,1)]:
            sig = apply_filters(base, t, hi, mtf, sess)
            OOS = tuple(x[si:] for x in bars)
            r = run(OOS, sig[si:], mode, a[si:], ks, kt, COST)
            wf = yrs_pos(bars, a, sig, mode, ks, kt)
            if not r:
                print(f'{name:22}{label:14}{"n/d":>8}'); continue
            print(f'{name:22}{label:14}{r["ret"]*100:>7.0f}%{r["pf"]:>6.2f}'
                  f'{r["maxdd"]*100:>6.0f}%{r["winrate"]*100:>4.0f}%{r["trades"]:>6d}{wf:>6}')
        print()


if __name__ == "__main__":
    main()
