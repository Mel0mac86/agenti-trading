#!/usr/bin/env python3
"""
money_management.py - Confronto onesto degli schemi di gestione del rischio sulla
sequenza REALE di trade di una strategia validata.

Schemi testati:
  - fixed     : rischio % costante (fixed fractional, compounding standard)
  - martingala: raddoppia il rischio dopo una PERDITA, reset dopo una vincita
  - antimart  : aumenta il rischio dopo una VINCITA (cap), reset dopo una perdita
  - tiered    : rischio cresce a scaglioni col capitale (compounding aggressivo)

Misura: capitale finale, max drawdown e soprattutto la PROBABILITA' DI ROVINA via
Monte Carlo (rimescolando l'ordine dei trade). Capitale iniziale 100, obiettivo 1M.

Uso: python3 money_management.py XAUUSD H1 --cost 0.15
"""
import os, sys, argparse, random
from backtest import (load, atr, ema, rsi, sma, rolling_std,
                      sig_ema_cross, sig_rsi_rev, sig_boll_rev, ATR_PERIOD, DATADIR)

START = 100.0
TARGET = 1_000_000.0
RUIN = 20.0          # rovina: capitale sceso sotto il 20% iniziale
MC = 3000            # simulazioni Monte Carlo

STRATS = {
    "XAUUSD": (lambda o,h,l,c: sig_ema_cross(o,h,l,c,20,50), "trend", 2.0, 0.0),
    "EURUSD": (lambda o,h,l,c: sig_rsi_rev(o,h,l,c,14,25,75), "rev",  1.5, 1.5),
}


def trade_R_sequence(pair, tf, cost):
    """Ritorna la lista dei R-multipli netti per trade della strategia validata."""
    fn, mode, ks, kt = STRATS[pair]
    t, o, h, l, c = load(os.path.join(DATADIR, f"{pair}_{tf}.csv"))
    a = atr(h, l, c, ATR_PERIOD)
    sig, _ = fn(o, h, l, c)
    n = len(c); pos = 0; entry = stop = target = risk = 0.0; Rs = []

    def book(px):
        nonlocal pos
        rg = (px-entry)/risk if pos > 0 else (entry-px)/risk
        Rs.append(rg - cost/risk); pos = 0

    for i in range(n-1):
        if pos != 0:
            if pos > 0:
                if l[i] <= stop: book(stop)
                elif mode == "rev" and target and h[i] >= target: book(target)
            else:
                if h[i] >= stop: book(stop)
                elif mode == "rev" and target and l[i] <= target: book(target)
        if pos != 0 and ((pos > 0 and sig[i] <= 0) or (pos < 0 and sig[i] >= 0)):
            book(o[i+1])
        if pos == 0 and sig[i] != 0 and a[i] and a[i] > 0:
            pos = sig[i]; entry = o[i+1]; risk = ks*a[i]
            if pos > 0: stop = entry-risk; target = entry+kt*a[i] if kt else 0.0
            else:       stop = entry+risk; target = entry-kt*a[i] if kt else 0.0
    return Rs


def simulate(Rs, scheme):
    """Esegue uno schema MM sulla sequenza Rs. Ritorna (capitale_finale, maxDD, rovinato)."""
    eq = START; peak = eq; mdd = 0.0
    f = scheme["f0"]
    for r in Rs:
        # rischio effettivo questo trade (frazione del capitale)
        risk_amt = f
        if risk_amt >= 1.0 and r < 0:      # un -1R con rischio >=100% azzera
            return 0.0, 1.0, True
        eq *= (1 + risk_amt * r)
        if eq <= RUIN:
            return eq, 1.0, True
        peak = max(peak, eq); mdd = max(mdd, (peak-eq)/peak)
        # aggiorna f secondo lo schema
        won = r > 0
        if scheme["type"] == "fixed":
            f = scheme["f0"]
        elif scheme["type"] == "martingala":
            f = scheme["f0"] if won else min(f * scheme["mult"], 4.0)
        elif scheme["type"] == "antimart":
            f = min(f * scheme["mult"], scheme["cap"]) if won else scheme["f0"]
        elif scheme["type"] == "tiered":
            # rischio cresce col capitale: +step ogni 10x, cap
            import math
            tiers = math.log10(max(eq/START, 1))
            f = min(scheme["f0"] + scheme["step"] * tiers, scheme["cap"])
    return eq, mdd, False


def montecarlo(Rs, scheme):
    fin = []; ruin = 0; hit = 0
    base = list(Rs)
    for _ in range(MC):
        random.shuffle(base)
        eq, mdd, r = simulate(base, scheme)
        fin.append(eq)
        if r: ruin += 1
        if eq >= TARGET: hit += 1
    fin.sort()
    median = fin[len(fin)//2]
    return median, ruin/MC, hit/MC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair"); ap.add_argument("tf")
    ap.add_argument("--cost", type=float, required=True)
    args = ap.parse_args()
    Rs = trade_R_sequence(args.pair.upper(), args.tf, args.cost)
    wr = sum(1 for r in Rs if r > 0)/len(Rs)
    print(f"# Money management — {args.pair} {args.tf} | {len(Rs)} trade | WR {wr*100:.0f}%")
    print(f"# Capitale {START:.0f} -> obiettivo {TARGET:,.0f} | rovina sotto {RUIN:.0f} | MC {MC}\n")

    schemes = [
        ("fixed 2%",          dict(type="fixed",      f0=0.02)),
        ("fixed 5%",          dict(type="fixed",      f0=0.05)),
        ("martingala x2",     dict(type="martingala", f0=0.01, mult=2.0)),
        ("antimart x1.5 c10%",dict(type="antimart",   f0=0.01, mult=1.5, cap=0.10)),
        ("tiered +1%/10x c8%",dict(type="tiered",     f0=0.01, step=0.01, cap=0.08)),
    ]
    print(f'{"schema":22}{"mediana fin.":>14}{"P(rovina)":>11}{"P(>=1M)":>9}')
    print("-"*56)
    for name, sc in schemes:
        med, pruin, phit = montecarlo(Rs, sc)
        print(f'{name:22}{med:>14,.0f}{pruin*100:>10.1f}%{phit*100:>8.1f}%')
    print()


if __name__ == "__main__":
    main()
