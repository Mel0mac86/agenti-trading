#!/usr/bin/env python3
"""
scalping_analysis.py - Analisi onesta dello scalping: quanto l'edge sopravvive
ai costi reali (spread + commissione + slippage) pagati su OGNI trade.

Sui timeframe bassi i trade sono tantissimi: il costo per trade diventa il fattore
dominante. Questo script mostra il rendimento OOS al crescere del costo, per oro
ed EUR/USD su M5 e M15.

Uso: python3 scalping_analysis.py
"""
import os
from backtest import (load, atr, run, sig_rsi_rev, sig_boll_rev,
                      ATR_PERIOD, DATADIR, START_EQUITY)

SPLIT = 2023

# (pair, TF, lista di costi/trade dal piu' ottimistico al piu' realistico)
CASES = [
    ("XAUUSD", "M5",  [0.08, 0.15, 0.25, 0.40]),
    ("XAUUSD", "M15", [0.08, 0.15, 0.25, 0.40]),
    ("EURUSD", "M5",  [0.00008, 0.00015, 0.00025, 0.00040]),
    ("EURUSD", "M15", [0.00008, 0.00015, 0.00025, 0.00040]),
]

STRATS = [
    ("RSI 7/20-80",  lambda o,h,l,c: sig_rsi_rev(o,h,l,c,7,20,80),  1.5, 1.5),
    ("RSI 14/25-75", lambda o,h,l,c: sig_rsi_rev(o,h,l,c,14,25,75), 1.5, 1.5),
    ("Boll 20/2.0",  lambda o,h,l,c: sig_boll_rev(o,h,l,c,20,2.0),  1.5, 1.5),
]


def main():
    print("# Analisi scalping: l'edge contro il muro dei costi (rendimento OOS 2023-24)\n")
    for pair, tf, costs in CASES:
        p = os.path.join(DATADIR, f"{pair}_{tf}.csv")
        if not os.path.exists(p):
            print(f"{pair} {tf}: dati mancanti\n"); continue
        t, o, h, l, c = load(p); a = atr(h, l, c, ATR_PERIOD)
        si = next((i for i, d in enumerate(t) if d.year >= SPLIT), len(t))
        OOS = (t[si:], o[si:], h[si:], l[si:], c[si:]); a_oo = a[si:]

        print(f"## {pair} {tf}")
        print(f'{"strategia":14}{"#trade":>8} | ' +
              " | ".join(f"costo {x}" for x in costs))
        for name, fn, ks, kt in STRATS:
            sig, mode = fn(OOS[1], OOS[2], OOS[3], OOS[4])
            cells = []; ntr = None
            for cost in costs:
                r = run(OOS, sig, mode, a_oo, ks, kt, cost)
                if not r:
                    cells.append("   n/d"); continue
                ntr = r["trades"]
                cells.append(f"{r['ret']*100:+7.0f}%")
            print(f'{name:14}{ntr if ntr else 0:>8} | ' + " | ".join(cells))
        print()


if __name__ == "__main__":
    main()
