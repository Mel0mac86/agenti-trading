#!/usr/bin/env python3
"""
walkforward.py - Verifica di robustezza ANNO PER ANNO delle strategie finaliste.

Un edge vero deve essere positivo in (quasi) tutti gli anni separatamente, non
solo in media su un singolo split. Parametri FISSI (non riottimizzati per anno):
e' il test piu' onesto contro l'overfitting.

Uso:
    python3 walkforward.py XAUUSD --strat ema2050 --tf H1
    python3 walkforward.py SPXUSD --strat donch55 --tf H4 --spread 50
    python3 walkforward.py SPXUSD --strat roc10 --tf D1 --spread 50
"""
import os, sys, argparse
from backtest import (load, atr, run, ema, sma, rolling_std, highest, lowest,
                      sig_ema_cross, sig_donchian, sig_roc, sig_boll_rev, sig_rsi_rev,
                      DEF_SPREAD_POINTS, DEF_POINT, DEF_COMM_PER_LOT, DEF_CONTRACT,
                      ATR_PERIOD, DATADIR)


# registro strategie: nome -> (funzione segnale, (k_stop, k_target))
STRATS = {
    "ema1030":  (lambda o,h,l,c: sig_ema_cross(o,h,l,c,10,30),        (2.0, 0.0)),
    "ema2050":  (lambda o,h,l,c: sig_ema_cross(o,h,l,c,20,50),        (2.0, 0.0)),
    "ema20100": (lambda o,h,l,c: sig_ema_cross(o,h,l,c,20,100),       (2.0, 0.0)),
    "ema50200": (lambda o,h,l,c: sig_ema_cross(o,h,l,c,50,200),       (2.0, 0.0)),
    "donch20":  (lambda o,h,l,c: sig_donchian(o,h,l,c,20),            (2.0, 0.0)),
    "donch40":  (lambda o,h,l,c: sig_donchian(o,h,l,c,40),            (2.0, 0.0)),
    "donch55":  (lambda o,h,l,c: sig_donchian(o,h,l,c,55),            (2.0, 0.0)),
    "roc10":    (lambda o,h,l,c: sig_roc(o,h,l,c,10),                 (2.0, 0.0)),
    "roc20":    (lambda o,h,l,c: sig_roc(o,h,l,c,20),                 (2.0, 0.0)),
    "boll20":   (lambda o,h,l,c: sig_boll_rev(o,h,l,c,20,2.0),        (1.5, 1.5)),
    "rsi2575":  (lambda o,h,l,c: sig_rsi_rev(o,h,l,c,14,25,75),       (1.5, 1.5)),
    "rsi3070":  (lambda o,h,l,c: sig_rsi_rev(o,h,l,c,14,30,70),       (1.5, 1.5)),
}


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
    ap.add_argument("--strat", default="ema2050", choices=sorted(STRATS))
    ap.add_argument("--tf", default="H1")
    ap.add_argument("--spread", type=int, default=DEF_SPREAD_POINTS)
    ap.add_argument("--cost", type=float, default=None, help="costo/trade in unita' di prezzo (override)")
    args = ap.parse_args()
    cost = args.cost if args.cost is not None else (args.spread * DEF_POINT + DEF_COMM_PER_LOT / DEF_CONTRACT)

    path = os.path.join(DATADIR, f"{args.pair.upper()}_{args.tf}.csv")
    if not os.path.exists(path):
        print(f"Manca {path}"); sys.exit(1)
    t, o, h, l, c = load(path)
    a = atr(h, l, c, ATR_PERIOD)
    bars = (t, o, h, l, c)
    years = sorted({dt.year for dt in t})
    fn, (ks, kt) = STRATS[args.strat]

    print(f"# Walk-forward {args.pair} {args.tf} | strat={args.strat} | "
          f"costo {cost:.3f} | parametri FISSI\n")
    print(f'{"Anno":6}{"ret":>9}{"PF":>7}{"DD":>7}{"WR":>6}{"#tr":>6}')
    wins = 0; tot = 0
    for y in years:
        yb, ya = slice_year(bars, a, y)
        if yb is None: continue
        s, mode = fn(yb[1], yb[2], yb[3], yb[4])
        r = run(yb, s, mode, ya, ks, kt, cost)
        if not r:
            print(f"{y:<6}{'n/d':>9}"); continue
        tot += 1; wins += 1 if r["ret"] > 0 else 0
        flag = "OK " if r["ret"] > 0 else "-- "
        print(f'{y:<6}{r["ret"]*100:>8.1f}%{r["pf"]:>7.2f}{r["maxdd"]*100:>6.1f}%'
              f'{r["winrate"]*100:>5.0f}%{r["trades"]:>6d}  {flag}')
    print(f"\n   -> anni positivi: {wins}/{tot}")


if __name__ == "__main__":
    main()
