#!/usr/bin/env python3
"""
portfolio.py - Combina le strategie ROBUSTE (verdi) in un portafoglio e misura
il beneficio di diversificazione (DD piu' basso, Sharpe piu' alto) rispetto ai
singoli edge.

Idea (data-driven, non overfitting): trend (metalli/indici) e mean-reversion
(forex) guadagnano in regimi opposti -> se poco correlati, il portafoglio
equal-risk ha un profilo rischio/rendimento migliore di ogni singola strategia.

Uso: python3 portfolio.py
"""
import os, math, datetime
from backtest import (load, atr, ema, rsi, sma, rolling_std,
                      sig_ema_cross, sig_rsi_rev, sig_boll_rev,
                      ATR_PERIOD, DATADIR)

RISK = 0.005   # 0,5% per trade

# I 4 strumenti VERDI (WF 4-5/5), tutti su H1, con la loro config validata e costo
GREEN = [
    ("XAUUSD", "H1", "trend", lambda o,h,l,c: sig_ema_cross(o,h,l,c,20,50), 2.0, 0.0, 0.15),
    ("EURUSD", "H1", "rev",   lambda o,h,l,c: sig_rsi_rev(o,h,l,c,14,25,75), 1.5, 1.5, 0.00015),
    ("USDCHF", "H1", "rev",   lambda o,h,l,c: sig_boll_rev(o,h,l,c,20,2.0),  1.5, 1.5, 0.00018),
    ("NSXUSD", "H1", "trend", lambda o,h,l,c: sig_ema_cross(o,h,l,c,10,30),  2.0, 0.0, 2.0),
]


def trades_monthly(bars, sig, mode, a, ks, kt, cost):
    """Esegue la strategia e ritorna i rendimenti mensili (% conto) come dict YYYY-MM."""
    t, o, h, l, c = bars; n = len(c)
    pos = 0; entry=stop=target=risk=0.0
    monthly = {}

    def book(exit_px, dt):
        nonlocal pos
        rg = (exit_px-entry)/risk if pos > 0 else (entry-exit_px)/risk
        rn = rg - cost/risk
        key = f"{dt.year}-{dt.month:02d}"
        monthly[key] = monthly.get(key, 0.0) + RISK * rn   # additivo nel mese
        pos = 0

    for i in range(n-1):
        if pos != 0:
            if pos > 0:
                if l[i] <= stop: book(stop, t[i])
                elif mode == "rev" and target and h[i] >= target: book(target, t[i])
            else:
                if h[i] >= stop: book(stop, t[i])
                elif mode == "rev" and target and l[i] <= target: book(target, t[i])
        # uscita su segnale opposto/neutro (coerente col motore run(): <=0 / >=0)
        if pos != 0 and ((pos > 0 and sig[i] <= 0) or (pos < 0 and sig[i] >= 0)):
            book(o[i+1], t[i+1])
        if pos == 0 and sig[i] != 0 and a[i] and a[i] > 0:
            pos = sig[i]; entry = o[i+1]; risk = ks*a[i]
            if pos > 0: stop = entry-risk; target = entry+kt*a[i] if kt else 0.0
            else:       stop = entry+risk; target = entry-kt*a[i] if kt else 0.0
    return monthly


def metrics(series):
    """series: lista di rendimenti mensili (frazione). Ritorna tot, maxDD, Sharpe annuo."""
    eq = 1.0; peak = 1.0; mdd = 0.0
    for r in series:
        eq *= (1+r); peak = max(peak, eq); mdd = max(mdd, (peak-eq)/peak)
    if len(series) < 2:
        return eq-1, mdd, 0.0
    m = sum(series)/len(series)
    var = sum((x-m)**2 for x in series)/len(series)
    sd = math.sqrt(var)
    sharpe = (m/sd*math.sqrt(12)) if sd > 0 else 0.0
    return eq-1, mdd, sharpe


def corr(a, b):
    n = len(a)
    ma, mb = sum(a)/n, sum(b)/n
    cov = sum((a[i]-ma)*(b[i]-mb) for i in range(n))/n
    sa = math.sqrt(sum((x-ma)**2 for x in a)/n)
    sb = math.sqrt(sum((x-mb)**2 for x in b)/n)
    return cov/(sa*sb) if sa > 0 and sb > 0 else 0.0


def main():
    monthlies = {}
    names = []
    for pair, tf, mode, fn, ks, kt, cost in GREEN:
        p = os.path.join(DATADIR, f"{pair}_{tf}.csv")
        if not os.path.exists(p):
            print(f"manca {pair} {tf}"); continue
        t, o, h, l, c = load(p)
        a = atr(h, l, c, ATR_PERIOD)
        sig, m = fn(o, h, l, c)
        monthlies[pair] = trades_monthly((t,o,h,l,c), sig, m, a, ks, kt, cost)
        names.append(pair)

    # asse temporale comune (unione dei mesi)
    all_keys = sorted({k for d in monthlies.values() for k in d})
    aligned = {p: [monthlies[p].get(k, 0.0) for k in all_keys] for p in names}
    # portafoglio equal-weight (media dei rendimenti mensili)
    port = [sum(aligned[p][i] for p in names)/len(names) for i in range(len(all_keys))]

    print(f"# Portafoglio dei 4 verdi | rischio {RISK*100:.1f}%/trade | {all_keys[0]} -> {all_keys[-1]}\n")
    print(f'{"Strumento":12}{"ret tot":>10}{"maxDD":>9}{"Sharpe":>8}')
    print("-"*39)
    for p in names:
        tot, mdd, sh = metrics(aligned[p])
        print(f'{p:12}{tot*100:>9.1f}%{mdd*100:>8.1f}%{sh:>8.2f}')
    ptot, pmdd, psh = metrics(port)
    print("-"*39)
    print(f'{"PORTAFOGLIO":12}{ptot*100:>9.1f}%{pmdd*100:>8.1f}%{psh:>8.2f}')
    avg_dd = sum(metrics(aligned[p])[1] for p in names)/len(names)
    avg_sh = sum(metrics(aligned[p])[2] for p in names)/len(names)
    print(f'\nMedia DD singoli: {avg_dd*100:.1f}%  ->  Portafoglio: {pmdd*100:.1f}%')
    print(f'Media Sharpe singoli: {avg_sh:.2f}  ->  Portafoglio: {psh:.2f}')

    print("\n## Matrice di correlazione (rendimenti mensili)")
    print(f'{"":8}' + "".join(f'{p:>9}' for p in names))
    for p in names:
        row = "".join(f'{corr(aligned[p], aligned[q]):>9.2f}' for q in names)
        print(f'{p:8}{row}')


if __name__ == "__main__":
    main()
