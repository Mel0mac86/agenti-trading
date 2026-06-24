#!/usr/bin/env python3
"""
backtest.py - Backtester multi-strategia / multi-timeframe per i dati MT4 generati
              da resample_mt4.py. Costi reali (spread + commissione) inclusi.

Obiettivo: selezionare strategie robuste classificandole su dati OUT-OF-SAMPLE
(mai usati per scegliere i parametri), non sul miglior numero in-sample.

NON e' uno Strategy Tester MT4: e' un modello bar-based (fill all'apertura della
barra successiva, stop/target valutati intrabar su high/low). Serve a fare lo
SHORTLIST; la validazione finale va fatta su MT4 in demo sul proprio broker.

Uso:
    python3 backtest.py XAUUSD
    python3 backtest.py XAUUSD --tf H1 H4 D1 --split 2023
"""
import os, sys, glob, argparse, datetime, math

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "mt4")

# ---- Assunzioni di costo (XAU/USD), modificabili da CLI ----
# Quotazione gold a 2 decimali: 1 point = 0.01. Spread 8 points = 0.08 (prezzo).
# Commissione 7$/lotto round-turn, lotto = 100 oz -> 0.07 $/oz = 0.07 in prezzo.
DEF_SPREAD_POINTS = 8
DEF_POINT = 0.01
DEF_COMM_PER_LOT = 7.0
DEF_CONTRACT = 100.0
RISK_PER_TRADE = 0.0075      # 0.75% equity
ATR_PERIOD = 14
START_EQUITY = 10000.0


# ============================ I/O ============================
def load(path):
    t, o, h, l, c = [], [], [], [], []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            p = line.strip().split(",")
            if len(p) < 6:
                continue
            dt = datetime.datetime.strptime(p[0] + " " + p[1], "%Y.%m.%d %H:%M")
            t.append(dt); o.append(float(p[2])); h.append(float(p[3]))
            l.append(float(p[4])); c.append(float(p[5]))
    return t, o, h, l, c


# ============================ Indicatori ============================
def ema(x, n):
    k = 2.0 / (n + 1); out = [None] * len(x); s = None
    for i, v in enumerate(x):
        s = v if s is None else v * k + s * (1 - k)
        out[i] = s
    return out

def sma(x, n):
    out = [None] * len(x); run = 0.0
    for i, v in enumerate(x):
        run += v
        if i >= n: run -= x[i - n]
        if i >= n - 1: out[i] = run / n
    return out

def rsi(c, n):
    out = [None] * len(c); g = l = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        up = max(d, 0.0); dn = max(-d, 0.0)
        if i <= n:
            g += up; l += dn
            if i == n:
                ag, al = g / n, l / n
                out[i] = 100 - 100 / (1 + (ag / al if al else 999))
        else:
            ag = (ag * (n - 1) + up) / n
            al = (al * (n - 1) + dn) / n
            out[i] = 100 - 100 / (1 + (ag / al if al else 999))
    return out

def atr(h, l, c, n):
    tr = [None] * len(c)
    for i in range(1, len(c)):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    out = [None] * len(c); s = None; cnt = 0; run = 0.0
    for i in range(1, len(c)):
        if tr[i] is None: continue
        cnt += 1; run += tr[i]
        if cnt == n: s = run / n; out[i] = s
        elif cnt > n: s = (s * (n - 1) + tr[i]) / n; out[i] = s
    return out

def rolling_std(x, n):
    out = [None] * len(x)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]; m = sum(w) / n
        out[i] = math.sqrt(sum((v - m) ** 2 for v in w) / n)
    return out

def highest(x, n):
    out = [None] * len(x)
    for i in range(n, len(x)):
        out[i] = max(x[i - n:i])
    return out

def lowest(x, n):
    out = [None] * len(x)
    for i in range(n, len(x)):
        out[i] = min(x[i - n:i])
    return out


# ============================ Strategie ============================
# Ognuna restituisce signal[i] in {+1,-1,0}: esposizione desiderata alla chiusura di i.
def sig_ema_cross(o, h, l, c, fast, slow):
    ef, es = ema(c, fast), ema(c, slow)
    s = [0] * len(c)
    for i in range(len(c)):
        if ef[i] is None or es[i] is None: continue
        s[i] = 1 if ef[i] > es[i] else -1
    return s, "trend"

def sig_donchian(o, h, l, c, n):
    hh, ll = highest(c, n), lowest(c, n)
    s = [0] * len(c); cur = 0
    for i in range(len(c)):
        if hh[i] is None: s[i] = cur; continue
        if c[i] > hh[i]: cur = 1
        elif c[i] < ll[i]: cur = -1
        s[i] = cur
    return s, "trend"

def sig_macd(o, h, l, c, f, sl, sg):
    ef, es = ema(c, f), ema(c, sl)
    macd = [(ef[i] - es[i]) if ef[i] is not None and es[i] is not None else None for i in range(len(c))]
    base = [m if m is not None else 0.0 for m in macd]
    signal = ema(base, sg)
    s = [0] * len(c)
    for i in range(len(c)):
        if macd[i] is None: continue
        s[i] = 1 if macd[i] > signal[i] else -1
    return s, "trend"

def sig_roc(o, h, l, c, n):
    s = [0] * len(c)
    for i in range(n, len(c)):
        s[i] = 1 if c[i] > c[i - n] else -1
    return s, "trend"

def sig_rsi_rev(o, h, l, c, n, os_, ob):
    r = rsi(c, n); s = [0] * len(c)
    for i in range(len(c)):
        if r[i] is None: continue
        if r[i] < os_: s[i] = 1
        elif r[i] > ob: s[i] = -1
    return s, "rev"

def sig_boll_rev(o, h, l, c, n, k):
    m, sd = sma(c, n), rolling_std(c, n); s = [0] * len(c)
    for i in range(len(c)):
        if m[i] is None or sd[i] is None: continue
        if c[i] < m[i] - k * sd[i]: s[i] = 1
        elif c[i] > m[i] + k * sd[i]: s[i] = -1
    return s, "rev"


# ============================ Motore di backtest ============================
def run(bars, signal, mode, atr_arr, k_stop, k_target, cost_price):
    """Esegue il backtest. Ritorna lista di R-multipli per trade ed equity curve."""
    t, o, h, l, c = bars
    n = len(c)
    pos = 0          # +1 long, -1 short, 0 flat
    entry = 0.0; risk_dist = 0.0; stop = 0.0; target = 0.0
    Rs = []
    equity = START_EQUITY; peak = equity; maxdd = 0.0; eq_curve = [equity]

    def close_trade(exit_price):
        nonlocal pos, equity, peak, maxdd
        r_gross = (exit_price - entry) / risk_dist if pos > 0 else (entry - exit_price) / risk_dist
        r_net = r_gross - cost_price / risk_dist
        Rs.append(r_net)
        equity *= (1 + RISK_PER_TRADE * r_net)
        peak = max(peak, equity)
        if peak > 0: maxdd = max(maxdd, (peak - equity) / peak)
        eq_curve.append(equity)
        pos = 0

    for i in range(n - 1):
        # gestione posizione aperta: stop/target intrabar sulla barra i
        if pos != 0:
            if pos > 0:
                if l[i] <= stop: close_trade(stop)
                elif mode == "rev" and target and h[i] >= target: close_trade(target)
            else:
                if h[i] >= stop: close_trade(stop)
                elif mode == "rev" and target and l[i] <= target: close_trade(target)
        # uscita su cambio segnale (al prossimo open)
        if pos != 0 and ((pos > 0 and signal[i] <= 0) or (pos < 0 and signal[i] >= 0)):
            close_trade(o[i + 1])
        # ingresso al prossimo open
        if pos == 0 and signal[i] != 0 and atr_arr[i] is not None and atr_arr[i] > 0:
            pos = signal[i]; entry = o[i + 1]
            risk_dist = k_stop * atr_arr[i]
            if pos > 0:
                stop = entry - risk_dist; target = entry + k_target * atr_arr[i] if k_target else 0.0
            else:
                stop = entry + risk_dist; target = entry - k_target * atr_arr[i] if k_target else 0.0

    if not Rs:
        return None
    wins = [r for r in Rs if r > 0]; losses = [r for r in Rs if r <= 0]
    gross_w = sum(wins); gross_l = -sum(losses)
    pf = gross_w / gross_l if gross_l > 0 else float("inf")
    exp = sum(Rs) / len(Rs)
    ret = equity / START_EQUITY - 1
    # Sharpe per-trade approssimato
    mean = exp; var = sum((r - mean) ** 2 for r in Rs) / len(Rs)
    sharpe = mean / math.sqrt(var) if var > 0 else 0.0
    return {"trades": len(Rs), "pf": pf, "exp_R": exp, "ret": ret,
            "maxdd": maxdd, "winrate": len(wins) / len(Rs), "sharpe": sharpe,
            "final_eq": equity}


# ============================ Griglie di test ============================
def strategies():
    grid = []
    for f, s in [(10, 30), (20, 50), (20, 100), (50, 200)]:
        grid.append(("EMA_cross", lambda o,h,l,c,F=f,S=s: sig_ema_cross(o,h,l,c,F,S), f"{f}/{s}", (2.0, 0.0)))
    for nn in [20, 40, 55]:
        grid.append(("Donchian", lambda o,h,l,c,N=nn: sig_donchian(o,h,l,c,N), f"N{nn}", (2.0, 0.0)))
    for f, s, g in [(12, 26, 9)]:
        grid.append(("MACD", lambda o,h,l,c,F=f,S=s,G=g: sig_macd(o,h,l,c,F,S,G), f"{f}/{s}/{g}", (2.0, 0.0)))
    for nn in [10, 20, 40]:
        grid.append(("ROC", lambda o,h,l,c,N=nn: sig_roc(o,h,l,c,N), f"N{nn}", (2.0, 0.0)))
    for p, a, b in [(14, 30, 70), (7, 20, 80), (14, 25, 75)]:
        grid.append(("RSI_rev", lambda o,h,l,c,P=p,A=a,B=b: sig_rsi_rev(o,h,l,c,P,A,B), f"{p}/{a}-{b}", (1.5, 1.5)))
    for nn, k in [(20, 2.0), (20, 2.5)]:
        grid.append(("Boll_rev", lambda o,h,l,c,N=nn,K=k: sig_boll_rev(o,h,l,c,N,K), f"{nn}/{k}", (1.5, 1.5)))
    return grid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--tf", nargs="+", default=["M15", "H1", "H4", "D1"])
    ap.add_argument("--split", type=int, default=2023, help="anno di inizio out-of-sample")
    ap.add_argument("--spread", type=int, default=DEF_SPREAD_POINTS)
    ap.add_argument("--min-trades", type=int, default=30)
    ap.add_argument("--max-dd", type=float, default=0.25)
    args = ap.parse_args()

    cost_price = args.spread * DEF_POINT + DEF_COMM_PER_LOT / DEF_CONTRACT
    print(f"# {args.pair} | costo/trade = {cost_price:.3f} (spread {args.spread}pt + comm) "
          f"| rischio {RISK_PER_TRADE*100:.2f}%/trade | OOS da {args.split}\n")

    results = []
    for tf in args.tf:
        path = os.path.join(DATADIR, f"{args.pair.upper()}_{tf}.csv")
        if not os.path.exists(path):
            print(f"  (manca {tf})"); continue
        t, o, h, l, c = load(path)
        a = atr(h, l, c, ATR_PERIOD)
        split_i = next((i for i, dt in enumerate(t) if dt.year >= args.split), len(t))
        IS = (t[:split_i], o[:split_i], h[:split_i], l[:split_i], c[:split_i])
        OOS = (t[split_i:], o[split_i:], h[split_i:], l[split_i:], c[split_i:])
        a_is, a_oos = a[:split_i], a[split_i:]

        for name, fn, ptxt, (ks, kt) in strategies():
            sig_is, mode = fn(IS[1], IS[2], IS[3], IS[4])
            r_is = run(IS, sig_is, mode, a_is, ks, kt, cost_price)
            sig_oos, _ = fn(OOS[1], OOS[2], OOS[3], OOS[4])
            r_oos = run(OOS, sig_oos, mode, a_oos, ks, kt, cost_price)
            if not r_is or not r_oos:
                continue
            results.append({"tf": tf, "name": name, "p": ptxt, "IS": r_is, "OOS": r_oos})

    # filtro robustezza: profittevole IN-SAMPLE e OUT-OF-SAMPLE, DD e trade accettabili
    def ok(x):
        return (x["IS"]["ret"] > 0 and x["OOS"]["ret"] > 0 and
                x["OOS"]["trades"] >= args.min_trades and
                x["OOS"]["maxdd"] <= args.max_dd)
    robust = [x for x in results if ok(x)]
    robust.sort(key=lambda x: x["OOS"]["ret"], reverse=True)

    hdr = f'{"TF":4} {"Strategia":10} {"Param":10} | {"OOS ret":>8} {"OOS PF":>6} {"DD":>6} {"WR":>5} {"#tr":>5} | {"IS ret":>7}'
    print("=== CLASSIFICA (robuste: profitto IS+OOS, DD<=%.0f%%, trade>=%d) ===" % (args.max_dd*100, args.min_trades))
    print(hdr); print("-" * len(hdr))
    for x in robust[:15]:
        O = x["OOS"]
        print(f'{x["tf"]:4} {x["name"]:10} {x["p"]:10} | {O["ret"]*100:7.1f}% {O["pf"]:6.2f} '
              f'{O["maxdd"]*100:5.1f}% {O["winrate"]*100:4.0f}% {O["trades"]:5d} | {x["IS"]["ret"]*100:6.1f}%')
    if not robust:
        print("Nessuna strategia robusta supera i filtri. (Meglio saperlo ora che coi soldi veri.)")
        print("\nTop 5 solo-OOS (NON robuste, indicativo):")
        results.sort(key=lambda x: x["OOS"]["ret"], reverse=True)
        for x in results[:5]:
            O = x["OOS"]
            print(f'  {x["tf"]:4} {x["name"]:10} {x["p"]:10} OOS {O["ret"]*100:6.1f}% PF{O["pf"]:.2f} DD{O["maxdd"]*100:.0f}% #{O["trades"]}')
    print()


if __name__ == "__main__":
    main()
