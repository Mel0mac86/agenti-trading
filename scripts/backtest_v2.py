#!/usr/bin/env python3
"""
backtest_v2.py - Versione potenziata di backtest.py.

Aggiunge meccanismi che mirano a WR piu' alto e DD piu' basso:
  - filtro di trend (EMA200): si opera solo nella direzione del trend di fondo;
  - take-profit su ATR (alza il win rate);
  - trailing stop su ATR (protegge i profitti, abbassa il DD);
  - filtro ADX (evita i mercati laterali per le strategie di trend);
  - setup "pullback-in-trend" (mean reversion solo a favore di trend = alto WR).

Stessa onesta' metodologica: costi reali, validazione OUT-OF-SAMPLE.
Backtest bar-based approssimato -> shortlist, non verita'. Conferma su MT4 demo.

Uso:
    python3 backtest_v2.py XAUUSD --tf M15 H1 H4 --split 2023
"""
import os, sys, argparse, math
from backtest import (load, ema, sma, rsi, atr, rolling_std, highest, lowest,
                      DEF_SPREAD_POINTS, DEF_POINT, DEF_COMM_PER_LOT, DEF_CONTRACT,
                      RISK_PER_TRADE, ATR_PERIOD, START_EQUITY, DATADIR)


# ---------------------- ADX (Wilder) ----------------------
def adx(h, l, c, n=14):
    L = len(c); tr = [0.0]*L; pdm = [0.0]*L; ndm = [0.0]*L
    for i in range(1, L):
        up = h[i]-h[i-1]; dn = l[i-1]-l[i]
        pdm[i] = up if (up > dn and up > 0) else 0.0
        ndm[i] = dn if (dn > up and dn > 0) else 0.0
        tr[i] = max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1]))
    out = [None]*L
    atr_ = pdi = ndi = None; adx_ = None; cnt = 0; str_=spdm=sndm=0.0; dxs=[]
    for i in range(1, L):
        cnt += 1
        if cnt <= n:
            str_ += tr[i]; spdm += pdm[i]; sndm += ndm[i]
            if cnt == n:
                atr_, pdi_, ndi_ = str_, spdm, sndm
        else:
            atr_ = atr_ - atr_/n + tr[i]
            pdi_ = pdi_ - pdi_/n + pdm[i]
            ndi_ = ndi_ - ndi_/n + ndm[i]
            pdi = 100*pdi_/atr_ if atr_ else 0
            ndi = 100*ndi_/atr_ if atr_ else 0
            dx = 100*abs(pdi-ndi)/(pdi+ndi) if (pdi+ndi) else 0
            dxs.append(dx)
            if len(dxs) == n:
                adx_ = sum(dxs)/n
            elif len(dxs) > n:
                adx_ = (adx_*(n-1)+dx)/n
            out[i] = adx_
    return out


# ---------------------- Motore con TP + trailing ----------------------
def run2(bars, signal, atr_arr, k_stop, k_tp, k_trail, cost_price):
    t, o, h, l, c = bars; n = len(c)
    pos = 0; entry=stop=target=risk=trail=fav=0.0
    Rs = []; equity = START_EQUITY; peak = equity; maxdd = 0.0

    def close(px):
        nonlocal pos, equity, peak, maxdd
        rg = (px-entry)/risk if pos > 0 else (entry-px)/risk
        rn = rg - cost_price/risk
        Rs.append(rn); equity *= (1 + RISK_PER_TRADE*rn)
        peak = max(peak, equity)
        if peak > 0: maxdd = max(maxdd, (peak-equity)/peak)
        pos = 0

    for i in range(n-1):
        if pos != 0:
            # aggiorna trailing
            if k_trail > 0:
                if pos > 0:
                    fav = max(fav, h[i]); cand = fav - k_trail*atr_arr[i] if atr_arr[i] else stop
                    stop = max(stop, cand)
                else:
                    fav = min(fav, l[i]); cand = fav + k_trail*atr_arr[i] if atr_arr[i] else stop
                    stop = min(stop, cand)
            # stop / target intrabar (stop ha priorita' prudenziale)
            if pos > 0:
                if l[i] <= stop: close(stop)
                elif target and h[i] >= target: close(target)
            else:
                if h[i] >= stop: close(stop)
                elif target and l[i] <= target: close(target)
        # uscita su segnale opposto
        if pos != 0 and ((pos > 0 and signal[i] < 0) or (pos < 0 and signal[i] > 0)):
            close(o[i+1])
        # ingresso
        if pos == 0 and signal[i] != 0 and atr_arr[i] and atr_arr[i] > 0:
            pos = signal[i]; entry = o[i+1]; risk = k_stop*atr_arr[i]; fav = entry
            if pos > 0:
                stop = entry-risk; target = entry+k_tp*atr_arr[i] if k_tp else 0.0
            else:
                stop = entry+risk; target = entry-k_tp*atr_arr[i] if k_tp else 0.0

    if not Rs: return None
    wins = [r for r in Rs if r > 0]; losses = [r for r in Rs if r <= 0]
    pf = sum(wins)/(-sum(losses)) if losses and sum(losses) < 0 else float("inf")
    exp = sum(Rs)/len(Rs); ret = equity/START_EQUITY-1
    var = sum((r-exp)**2 for r in Rs)/len(Rs); sharpe = exp/math.sqrt(var) if var > 0 else 0
    return {"trades": len(Rs), "pf": pf, "ret": ret, "maxdd": maxdd,
            "winrate": len(wins)/len(Rs), "sharpe": sharpe}


# ---------------------- Strategie potenziate ----------------------
def make_strats():
    S = []
    # EMA cross 20/50 con filtro trend EMA200 + trailing
    def ema_filt(o,h,l,c, trail):
        ef, es, e2 = ema(c,20), ema(c,50), ema(c,200)
        s = [0]*len(c)
        for i in range(len(c)):
            if None in (ef[i],es[i],e2[i]): continue
            up = ef[i] > es[i] and c[i] > e2[i]
            dn = ef[i] < es[i] and c[i] < e2[i]
            s[i] = 1 if up else (-1 if dn else 0)
        return s
    S.append(("EMAtrend+trail", lambda o,h,l,c: ema_filt(o,h,l,c,2.5), "20/50/200", dict(k_stop=2.0,k_tp=0,k_trail=2.5)))
    S.append(("EMAtrend",       lambda o,h,l,c: ema_filt(o,h,l,c,0),   "20/50/200", dict(k_stop=2.0,k_tp=0,k_trail=0)))
    # EMAtrend con take-profit a R fisso (banca le vincite -> WR piu' alto)
    for tp in [1.5, 2.5, 4.0]:
        S.append(("EMAtrend+TP", lambda o,h,l,c: ema_filt(o,h,l,c,0), f"20/50/200 tp{tp}", dict(k_stop=2.0,k_tp=tp,k_trail=0)))

    # Donchian con filtro EMA200 + trailing
    def donch_filt(o,h,l,c,N):
        hh, ll, e2 = highest(c,N), lowest(c,N), ema(c,200)
        s=[0]*len(c); cur=0
        for i in range(len(c)):
            if hh[i] is None or e2[i] is None: s[i]=cur; continue
            if c[i]>hh[i] and c[i]>e2[i]: cur=1
            elif c[i]<ll[i] and c[i]<e2[i]: cur=-1
            s[i]=cur
        return s
    for N in [20,40]:
        S.append((f"Donch+trend", lambda o,h,l,c,N=N: donch_filt(o,h,l,c,N), f"N{N}/200", dict(k_stop=2.0,k_tp=0,k_trail=3.0)))

    # Pullback-in-trend: trend con EMA200, ingresso su RSI in eccesso, TP su ATR (alto WR)
    def pullback(o,h,l,c,rn,buy,sell):
        r, e2 = rsi(c,rn), ema(c,200); s=[0]*len(c)
        for i in range(len(c)):
            if r[i] is None or e2[i] is None: continue
            if c[i] > e2[i] and r[i] < buy: s[i] = 1
            elif c[i] < e2[i] and r[i] > sell: s[i] = -1
        return s
    for rn,b,se in [(14,40,60),(7,35,65),(14,45,55)]:
        for tp,sl in [(2.0,1.5),(3.0,2.0)]:
            S.append((f"Pullback", lambda o,h,l,c,rn=rn,b=b,se=se: pullback(o,h,l,c,rn,b,se),
                      f"r{rn}/{b}-{se} tp{tp}/sl{sl}", dict(k_stop=sl,k_tp=tp,k_trail=0)))

    # EMA cross + filtro ADX (solo trend forti)
    def ema_adx(o,h,l,c,th):
        ef, es, ax = ema(c,20), ema(c,50), adx(h,l,c,14); s=[0]*len(c)
        for i in range(len(c)):
            if None in (ef[i],es[i]) or ax[i] is None: continue
            if ax[i] < th: continue
            s[i] = 1 if ef[i] > es[i] else -1
        return s
    for th in [20,25]:
        S.append((f"EMA+ADX", lambda o,h,l,c,th=th: ema_adx(o,h,l,c,th), f"20/50 adx>{th}", dict(k_stop=2.0,k_tp=0,k_trail=2.5)))
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair"); ap.add_argument("--tf", nargs="+", default=["M15","H1","H4"])
    ap.add_argument("--split", type=int, default=2023)
    ap.add_argument("--spread", type=int, default=DEF_SPREAD_POINTS)
    ap.add_argument("--min-trades", type=int, default=30)
    args = ap.parse_args()
    cost = args.spread*DEF_POINT + DEF_COMM_PER_LOT/DEF_CONTRACT
    print(f"# {args.pair} v2 | costo/trade {cost:.3f} | rischio {RISK_PER_TRADE*100:.2f}% | OOS da {args.split}\n")

    res = []
    for tf in args.tf:
        p = os.path.join(DATADIR, f"{args.pair.upper()}_{tf}.csv")
        if not os.path.exists(p): print(f"  (manca {tf})"); continue
        t,o,h,l,c = load(p); a = atr(h,l,c,ATR_PERIOD)
        si = next((i for i,dt in enumerate(t) if dt.year >= args.split), len(t))
        IS=(t[:si],o[:si],h[:si],l[:si],c[:si]); a_is=a[:si]
        OOS=(t[si:],o[si:],h[si:],l[si:],c[si:]); a_oos=a[si:]
        for name, fn, ptxt, kw in make_strats():
            s_is = fn(IS[1],IS[2],IS[3],IS[4]); r_is = run2(IS,s_is,a_is,cost_price=cost,**kw)
            s_oo = fn(OOS[1],OOS[2],OOS[3],OOS[4]); r_oo = run2(OOS,s_oo,a_oos,cost_price=cost,**kw)
            if not r_is or not r_oo: continue
            res.append({"tf":tf,"name":name,"p":ptxt,"IS":r_is,"OOS":r_oo})

    rob = [x for x in res if x["IS"]["ret"]>0 and x["OOS"]["ret"]>0 and x["OOS"]["trades"]>=args.min_trades]
    # punteggio bilanciato: premia ritorno e WR, penalizza DD
    def score(x):
        O=x["OOS"]; return O["ret"]*100 + O["winrate"]*40 - O["maxdd"]*120
    rob.sort(key=score, reverse=True)

    hdr=f'{"TF":4} {"Strategia":15} {"Param":18} | {"OOS ret":>8} {"PF":>5} {"DD":>6} {"WR":>5} {"#tr":>5} | {"IS ret":>7}'
    print("=== CLASSIFICA v2 (ordinata per ritorno + WR - DD) ===")
    print(hdr); print("-"*len(hdr))
    for x in rob[:15]:
        O=x["OOS"]
        print(f'{x["tf"]:4} {x["name"]:15} {x["p"]:18} | {O["ret"]*100:7.1f}% {O["pf"]:5.2f} '
              f'{O["maxdd"]*100:5.1f}% {O["winrate"]*100:4.0f}% {O["trades"]:5d} | {x["IS"]["ret"]*100:6.1f}%')
    print()

    # diagnostica: tutti i candidati con ritorno OOS>0 ordinati per WIN RATE
    pos = [x for x in res if x["OOS"]["ret"] > 0 and x["OOS"]["trades"] >= args.min_trades]
    pos.sort(key=lambda x: x["OOS"]["winrate"], reverse=True)
    print("=== Top per WIN RATE (OOS ret>0, #tr>=%d) ===" % args.min_trades)
    print(hdr); print("-"*len(hdr))
    for x in pos[:12]:
        O=x["OOS"]
        print(f'{x["tf"]:4} {x["name"]:15} {x["p"]:18} | {O["ret"]*100:7.1f}% {O["pf"]:5.2f} '
              f'{O["maxdd"]*100:5.1f}% {O["winrate"]*100:4.0f}% {O["trades"]:5d} | {x["IS"]["ret"]*100:6.1f}%')
    print()


if __name__ == "__main__":
    main()
