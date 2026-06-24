#!/usr/bin/env python3
"""
walkforward.py - Verifica di robustezza ANNO PER ANNO delle strategie finaliste.

Un edge vero deve essere positivo in (quasi) tutti gli anni separatamente, non
solo in media su un singolo split. Parametri FISSI (non riottimizzati per anno):
e' il test piu' onesto contro l'overfitting.

Uso:
    python3 walkforward.py XAUUSD --tf H1
"""
import os, sys, argparse
from backtest import (load, atr, run, ema, sig_ema_cross,
                      DEF_SPREAD_POINTS, DEF_POINT, DEF_COMM_PER_LOT, DEF_CONTRACT,
                      ATR_PERIOD, DATADIR)


def sig_ema_trend(o, h, l, c):
    """EMA 20/50 con filtro di trend EMA200 (long solo sopra, short solo sotto)."""
    ef, es, e2 = ema(c, 20), ema(c, 50), ema(c, 200)
    s = [0] * len(c)
    for i in range(len(c)):
        if None in (ef[i], es[i], e2[i]):
            continue
        if ef[i] > es[i] and c[i] > e2[i]:
            s[i] = 1
        elif ef[i] < es[i] and c[i] < e2[i]:
            s[i] = -1
    return s, "trend"


def slice_year(bars, a, year):
    t, o, h, l, c = bars
    idx = [i for i, dt in enumerate(t) if dt.year == year]
    if not idx:
        return None, None
    a_, b_ = idx[0], idx[-1] + 1
    return (t[a_:b_], o[a_:b_], h[a_:b_], l[a_:b_], c[a_:b_]), a[a_:b_]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--tf", default="H1")
    ap.add_argument("--spread", type=int, default=DEF_SPREAD_POINTS)
    args = ap.parse_args()
    cost = args.spread * DEF_POINT + DEF_COMM_PER_LOT / DEF_CONTRACT

    path = os.path.join(DATADIR, f"{args.pair.upper()}_{args.tf}.csv")
    if not os.path.exists(path):
        print(f"Manca {path}"); sys.exit(1)
    t, o, h, l, c = load(path)
    a = atr(h, l, c, ATR_PERIOD)
    bars = (t, o, h, l, c)
    years = sorted({dt.year for dt in t})

    strats = [
        ("EMA 20/50",        lambda o,h,l,c: sig_ema_cross(o,h,l,c,20,50)),
        ("EMA 20/50 +EMA200", sig_ema_trend),
    ]

    print(f"# Walk-forward {args.pair} {args.tf} | costo {cost:.3f} | parametri FISSI\n")
    for name, fn in strats:
        print(f"### {name}")
        print(f'{"Anno":6}{"ret":>9}{"PF":>7}{"DD":>7}{"WR":>6}{"#tr":>6}')
        wins = 0; tot = 0
        for y in years:
            yb, ya = slice_year(bars, a, y)
            if yb is None: continue
            s, mode = fn(yb[1], yb[2], yb[3], yb[4])
            r = run(yb, s, mode, ya, 2.0, 0.0, cost)
            if not r:
                print(f"{y:<6}{'n/d':>9}"); continue
            tot += 1; wins += 1 if r["ret"] > 0 else 0
            flag = "OK " if r["ret"] > 0 else "-- "
            print(f'{y:<6}{r["ret"]*100:>8.1f}%{r["pf"]:>7.2f}{r["maxdd"]*100:>6.1f}%'
                  f'{r["winrate"]*100:>5.0f}%{r["trades"]:>6d}  {flag}')
        print(f"   -> anni positivi: {wins}/{tot}\n")


if __name__ == "__main__":
    main()
