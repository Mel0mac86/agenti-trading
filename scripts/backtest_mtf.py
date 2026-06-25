#!/usr/bin/env python3
"""
backtest_mtf.py - Test multi-timeframe: filtra i segnali su H1 con il trend di un
timeframe superiore (D1). Verifica se l'allineamento MTF migliora i 4 verdi.

Filtro MTF (no look-ahead): per ogni barra H1 si usa l'ULTIMA barra D1 gia' chiusa.
Trend D1 = segno di (close - EMA(D1, N)). Si tiene il segnale H1 solo se concorde
col trend D1; altrimenti si resta flat.

Uso: python3 backtest_mtf.py
"""
import os, datetime
from backtest import (load, atr, ema, rsi, sma, rolling_std, run,
                      sig_ema_cross, sig_rsi_rev, sig_boll_rev,
                      ATR_PERIOD, DATADIR)

SPLIT = 2023
HI_TF = "D1"
HI_EMA = 50

# i 4 verdi: (pair, base_signal_fn, ks, kt, cost)
GREEN = [
    ("XAUUSD", lambda o,h,l,c: sig_ema_cross(o,h,l,c,20,50), 2.0, 0.0, 0.15),
    ("NSXUSD", lambda o,h,l,c: sig_ema_cross(o,h,l,c,10,30), 2.0, 0.0, 2.0),
    ("EURUSD", lambda o,h,l,c: sig_rsi_rev(o,h,l,c,14,25,75), 1.5, 1.5, 0.00015),
    ("USDCHF", lambda o,h,l,c: sig_boll_rev(o,h,l,c,20,2.0),  1.5, 1.5, 0.00018),
]


def higher_trend_on_h1(h1_t, pair):
    """Ritorna, per ogni barra H1, il trend D1 (+1/-1/0) dell'ultima D1 chiusa."""
    p = os.path.join(DATADIR, f"{pair}_{HI_TF}.csv")
    t, o, h, l, c = load(p)
    e = ema(c, HI_EMA)
    trend = [0]*len(c)
    for i in range(len(c)):
        if e[i] is None: continue
        trend[i] = 1 if c[i] > e[i] else -1
    dur = datetime.timedelta(minutes=1440)  # D1
    out = [0]*len(h1_t); j = -1
    for i, tt in enumerate(h1_t):
        while j+1 < len(t) and t[j+1] + dur <= tt:
            j += 1
        if j >= 0:
            out[i] = trend[j]
    return out


def gate(sig, hi):
    """Tiene il segnale solo se concorde col trend D1."""
    g = [0]*len(sig)
    for i in range(len(sig)):
        if (sig[i] > 0 and hi[i] > 0) or (sig[i] < 0 and hi[i] < 0):
            g[i] = sig[i]
    return g


def metrics_split(bars, a, sigfull, mode, ks, kt, cost):
    t = bars[0]
    si = next((i for i, d in enumerate(t) if d.year >= SPLIT), len(t))
    OOS = tuple(x[si:] for x in bars)
    r = run(OOS, sigfull[si:], mode, a[si:], ks, kt, cost)
    return r


def years_pos(bars, a, sigfull, mode, ks, kt, cost):
    t = bars[0]; yrs = sorted({d.year for d in t}); w = tot = 0
    for y in yrs:
        idx = [i for i, d in enumerate(t) if d.year == y]
        if not idx: continue
        s, e = idx[0], idx[-1]+1
        r = run(tuple(x[s:e] for x in bars), sigfull[s:e], mode, a[s:e], ks, kt, cost)
        if r: tot += 1; w += 1 if r["ret"] > 0 else 0
    return f"{w}/{tot}"


def main():
    print(f"# Multi-timeframe: filtro trend {HI_TF} EMA{HI_EMA} su segnali H1\n")
    hdr = f'{"Pair":8}{"versione":8}{"OOS ret":>9}{"PF":>6}{"DD":>7}{"WR":>5}{"#tr":>6}{"WF":>6}'
    print(hdr); print("-"*len(hdr))
    for pair, fn, ks, kt, cost in GREEN:
        p = os.path.join(DATADIR, f"{pair}_H1.csv")
        if not os.path.exists(p):
            print(f"{pair}: manca H1"); continue
        t, o, h, l, c = load(p); a = atr(h, l, c, ATR_PERIOD)
        bars = (t, o, h, l, c)
        sig, mode = fn(o, h, l, c)
        hi = higher_trend_on_h1(t, pair)
        gsig = gate(sig, hi)
        for label, s in [("base", sig), ("MTF", gsig)]:
            r = metrics_split(bars, a, s, mode, ks, kt, cost)
            wf = years_pos(bars, a, s, mode, ks, kt, cost)
            if not r:
                print(f"{pair:8}{label:8}{'n/d':>9}"); continue
            print(f'{pair:8}{label:8}{r["ret"]*100:>8.1f}%{r["pf"]:>6.2f}'
                  f'{r["maxdd"]*100:>6.1f}%{r["winrate"]*100:>4.0f}%{r["trades"]:>6d}{wf:>6}')
        print()


if __name__ == "__main__":
    main()
