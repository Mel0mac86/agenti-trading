#!/usr/bin/env python3
"""
run_all.py - Batch su piu' strumenti: download -> resample -> backtest -> walk-forward.

Per ogni pair trova la migliore strategia ROBUSTA (profitto in-sample E out-of-sample)
e ne misura la robustezza anno per anno. Produce una tabella consolidata in
docs/risultati-tutti-i-pair.md.

Costi per strumento APPROSSIMATI (in unita' di prezzo): servono per lo shortlist,
la validazione finale va fatta su MT4 demo sul proprio broker.

Uso: python3 run_all.py
"""
import os, sys, time, datetime
import histdata_download as dl
import resample_mt4 as rs
from backtest import (load, atr, run, strategies, ATR_PERIOD, DATADIR, START_EQUITY)

YEARS = [2020, 2021, 2022, 2023, 2024]
TFS = ["M15", "H1", "H4", "D1"]
SPLIT = 2023
RAWDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")

# pair -> costo/trade approssimato (unita' di prezzo dello strumento)
PAIRS = {
    # forex major
    "EURUSD": 0.00015, "GBPUSD": 0.00018, "AUDUSD": 0.00016,
    "USDCHF": 0.00018, "USDCAD": 0.00020, "NZDUSD": 0.00022,
    "USDJPY": 0.020,
    # metalli
    "XAUUSD": 0.15, "XAGUSD": 0.04,
    # indici
    "SPXUSD": 0.6, "NSXUSD": 2.0, "GRXEUR": 3.0,
}


def ensure_data(pair):
    """Scarica gli anni mancanti (con retry) e rigenera i timeframe."""
    for y in YEARS:
        csv = os.path.join(RAWDIR, f"DAT_ASCII_{pair}_M1_{y}.csv")
        if os.path.exists(csv):
            continue
        for att in range(4):
            try:
                dl.download(pair, y)
                print(f"   dl {pair} {y} OK"); break
            except Exception as e:
                print(f"   dl {pair} {y} retry {att+1}: {str(e)[:60]}")
                time.sleep(2 * (att + 1))
        time.sleep(0.5)
    # resample
    import glob
    paths = glob.glob(os.path.join(RAWDIR, f"DAT_ASCII_{pair}_M1_*.csv"))
    if not paths:
        return False
    rows = rs.read_m1(paths, 0)
    os.makedirs(rs.OUTDIR, exist_ok=True)
    for tf in TFS:
        bars = rows if tf == "M1" else rs.resample(rows, rs.TF_MIN[tf])
        rs.write_mt4(bars, os.path.join(rs.OUTDIR, f"{pair}_{tf}.csv"))
    return True


def years_positive(bars, a, fn, ks, kt, cost):
    """Walk-forward: quanti anni su 5 sono positivi (parametri fissi)."""
    t = bars[0]
    yrs = sorted({d.year for d in t})
    wins = tot = 0
    for y in yrs:
        idx = [i for i, d in enumerate(t) if d.year == y]
        if not idx:
            continue
        s, e = idx[0], idx[-1] + 1
        yb = tuple(x[s:e] for x in bars)
        sig, mode = fn(yb[1], yb[2], yb[3], yb[4])
        r = run(yb, sig, mode, a[s:e], ks, kt, cost)
        if r:
            tot += 1; wins += 1 if r["ret"] > 0 else 0
    return wins, tot


def analyze(pair, cost):
    """Trova la migliore strategia robusta per il pair su tutti i TF."""
    best = None
    for tf in TFS:
        p = os.path.join(DATADIR, f"{pair}_{tf}.csv")
        if not os.path.exists(p):
            continue
        t, o, h, l, c = load(p)
        a = atr(h, l, c, ATR_PERIOD)
        si = next((i for i, d in enumerate(t) if d.year >= SPLIT), len(t))
        IS = (t[:si], o[:si], h[:si], l[:si], c[:si]); a_is = a[:si]
        OOS = (t[si:], o[si:], h[si:], l[si:], c[si:]); a_oo = a[si:]
        for name, fn, ptxt, (ks, kt) in strategies():
            s_is, mode = fn(IS[1], IS[2], IS[3], IS[4]); r_is = run(IS, s_is, mode, a_is, ks, kt, cost)
            s_oo, _ = fn(OOS[1], OOS[2], OOS[3], OOS[4]); r_oo = run(OOS, s_oo, mode, a_oo, ks, kt, cost)
            if not r_is or not r_oo:
                continue
            # robusto: profitto IS+OOS, DD accettabile, trade sufficienti, no numeri assurdi
            if (r_is["ret"] > 0 and r_oo["ret"] > 0 and r_oo["maxdd"] <= 0.25
                    and r_oo["trades"] >= 30 and r_oo["ret"] < 5.0):
                cand = dict(tf=tf, name=name, p=ptxt, fn=fn, ks=ks, kt=kt,
                            bars=(t, o, h, l, c), atr=a, **{"r": r_oo})
                if best is None or r_oo["ret"] > best["r"]["ret"]:
                    best = cand
    if not best:
        return None
    wins, tot = years_positive(best["bars"], best["atr"], best["fn"], best["ks"], best["kt"], cost)
    best["wf"] = f"{wins}/{tot}"
    return best


def main():
    rows_out = []
    for pair, cost in PAIRS.items():
        print(f"== {pair} (costo {cost}) ==")
        try:
            if not ensure_data(pair):
                print(f"   dati mancanti, salto"); continue
            b = analyze(pair, cost)
            if not b:
                rows_out.append((pair, "—", "—", None, None, None, None, "—"))
                print(f"   nessuna strategia robusta")
                continue
            R = b["r"]
            rows_out.append((pair, b["name"], b["tf"], R["ret"], R["pf"],
                             R["maxdd"], R["winrate"], b["wf"]))
            print(f"   BEST: {b['name']} {b['p']} {b['tf']} | OOS {R['ret']*100:.1f}% "
                  f"PF{R['pf']:.2f} DD{R['maxdd']*100:.1f}% WR{R['winrate']*100:.0f}% WF{b['wf']}")
        except Exception as e:
            print(f"   ERRORE {pair}: {e}")

    # scrivi markdown
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs",
                       "risultati-tutti-i-pair.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Risultati backtest — tutti i pair\n\n")
        f.write(f"Generato da `scripts/run_all.py` il {datetime.date.today()}. "
                "Dati HistData 2020–2024, costi approssimati per strumento, "
                "split OOS dal 2023, walk-forward (WF) = anni positivi su 5.\n\n")
        f.write("> ⚠️ Backtest bar-based approssimato → shortlist. Conferma su MT4 demo.\n")
        f.write("> La 'migliore' è la più redditizia OOS tra quelle ROBUSTE "
                "(profitto IS+OOS, DD≤25%, ≥30 trade, no artefatti).\n\n")
        f.write("| Pair | Migliore strategia | TF | OOS ret | PF | DD | WR | WF |\n")
        f.write("|------|--------------------|----|--------:|----:|----:|----:|:--:|\n")
        for p, name, tf, ret, pf, dd, wr, wf in rows_out:
            if ret is None:
                f.write(f"| {p} | {name} | {tf} | — | — | — | — | {wf} |\n")
            else:
                f.write(f"| {p} | {name} | {tf} | {ret*100:.1f}% | {pf:.2f} | "
                        f"{dd*100:.1f}% | {wr*100:.0f}% | {wf} |\n")
    print(f"\nScritto {out}")


if __name__ == "__main__":
    main()
