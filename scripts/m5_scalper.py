#!/usr/bin/env python3
"""
m5_scalper.py - Ricerca della MIGLIORE strategia scalper pura su M5 (single TF,
niente multi-timeframe). Sweep ampio, costi reali, validazione walk-forward.

Strategie scalper: reversion (RSI, Bollinger) e breakout (Donchian) su M5, con
filtro di sessione opzionale (ore liquide). Nessun filtro da timeframe superiore.

Uso:
    python3 m5_scalper.py XAUUSD --cost 0.20
    python3 m5_scalper.py EURUSD --cost 0.00020
"""
import os, sys, argparse
from backtest import (load, atr, run, ema, rsi, sma, rolling_std,
                      sig_rsi_rev, sig_boll_rev, sig_donchian,
                      ATR_PERIOD, DATADIR)

SPLIT = 2023
SESS_START, SESS_END = 3, 12   # finestra liquida (EST): Londra+overlap NY


def sess_filter(sig, times):
    g = list(sig)
    for i in range(len(g)):
        if g[i] and not (SESS_START <= times[i].hour < SESS_END):
            g[i] = 0
    return g


def build():
    S = []
    for p in [5, 7, 14]:
        for a, b in [(20, 80), (25, 75), (10, 90)]:
            for ks, kt in [(1.0, 1.0), (1.5, 1.5), (1.0, 1.5)]:
                S.append((f"RSI{p} {a}/{b} s{ks}t{kt}", "rev",
                          lambda o,h,l,c,p=p,a=a,b=b: sig_rsi_rev(o,h,l,c,p,a,b), ks, kt))
    for p in [10, 20]:
        for d in [1.5, 2.0, 2.5]:
            for ks, kt in [(1.0, 1.0), (1.5, 1.5)]:
                S.append((f"Boll{p}/{d} s{ks}t{kt}", "rev",
                          lambda o,h,l,c,p=p,d=d: sig_boll_rev(o,h,l,c,p,d), ks, kt))
    for n in [10, 20, 40]:
        for ks in [1.5, 2.0]:
            S.append((f"Donch{n} s{ks}", "trend",
                      lambda o,h,l,c,n=n: sig_donchian(o,h,l,c,n), ks, 0.0))
    return S


def yrs_pos(bars, a, sig, mode, ks, kt, cost):
    t = bars[0]; w = tot = 0
    for y in sorted({d.year for d in t}):
        idx = [i for i, d in enumerate(t) if d.year == y]
        if not idx: continue
        s, e = idx[0], idx[-1]+1
        r = run(tuple(x[s:e] for x in bars), sig[s:e], mode, a[s:e], ks, kt, cost)
        if r: tot += 1; w += 1 if r["ret"] > 0 else 0
    return w, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--cost", type=float, required=True)
    args = ap.parse_args()
    pair = args.pair.upper()
    p = os.path.join(DATADIR, f"{pair}_M5.csv")
    if not os.path.exists(p):
        print(f"manca {pair}_M5.csv"); return
    t, o, h, l, c = load(p); a = atr(h, l, c, ATR_PERIOD)
    bars = (t, o, h, l, c)
    si = next((i for i, d in enumerate(t) if d.year >= SPLIT), len(t))

    results = []
    for name, mode, fn, ks, kt in build():
        base = fn(o, h, l, c)[0]
        for slabel, sig in [("no-sess", base), ("sess", sess_filter(base, t))]:
            r = run(tuple(x[si:] for x in bars), sig[si:], mode, a[si:], ks, kt, args.cost)
            if not r or r["trades"] < 30 or r["ret"] > 5.0:   # scarta artefatti
                continue
            w, tot = yrs_pos(bars, a, sig, mode, ks, kt, args.cost)
            results.append((name, slabel, r, w, tot))

    # ordina per robustezza (anni positivi) poi per rendimento OOS
    results.sort(key=lambda x: (x[3], x[2]["ret"]), reverse=True)
    print(f"# Migliore scalper M5 PURO (single TF) — {pair} costo {args.cost} | OOS da {SPLIT}\n")
    hdr = f'{"strategia":22}{"sess":9}{"OOSret":>8}{"PF":>6}{"DD":>7}{"WR":>5}{"#tr":>6}{"WF":>6}'
    print(hdr); print("-"*len(hdr))
    for name, sl, r, w, tot in results[:12]:
        print(f'{name:22}{sl:9}{r["ret"]*100:>7.0f}%{r["pf"]:>6.2f}'
              f'{r["maxdd"]*100:>6.0f}%{r["winrate"]*100:>4.0f}%{r["trades"]:>6d}{f"{w}/{tot}":>6}')
    if not results:
        print("Nessuna strategia con >=30 trade.")
    print()


if __name__ == "__main__":
    main()
