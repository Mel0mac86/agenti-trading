#!/usr/bin/env python3
"""
resample_mt4.py - Converte le barre M1 di HistData nei vari timeframe,
in formato importabile dallo Strategy Tester / History Center di MT4.

Input  : uno o piu' CSV M1 di HistData  (YYYYMMDD HHMMSS;O;H;L;C;Vol, separatore ';')
Output : un CSV per timeframe in formato MT4  (YYYY.MM.DD,HH:MM,O,H,L,C,Vol)

Uso:
    python3 resample_mt4.py XAUUSD                 # tutti i M1 in data/raw del simbolo
    python3 resample_mt4.py XAUUSD --tf M5 M15 H1 H4 D1
    python3 resample_mt4.py XAUUSD --tz 7          # sposta EST->EET (+7h) per allineare al broker

Timeframe supportati: M1 M5 M15 M30 H1 H4 D1
Default: M5 M15 M30 H1 H4 D1

Nota fuso: i dati HistData sono in EST (UTC-5) fisso. Se il tuo broker MT4 e'
in EET (UTC+2, +3 con ora legale) usa --tz 7 (o 8). Per un backtest interno e'
spesso accettabile lasciare 0, purche' la stessa convenzione valga ovunque.
"""
import sys, os, glob, argparse, datetime

TF_MIN = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
RAWDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "mt4")


def read_m1(paths, tz_shift_hours=0):
    """Legge e concatena i CSV M1 (ordinati), restituendo tuple ordinate per tempo."""
    shift = datetime.timedelta(hours=tz_shift_hours)
    rows = []
    for p in sorted(paths):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) < 5:
                    continue
                ts, o, h, l, c = parts[0], parts[1], parts[2], parts[3], parts[4]
                vol = parts[5] if len(parts) > 5 else "0"
                dt = datetime.datetime.strptime(ts, "%Y%m%d %H%M%S") + shift
                rows.append((dt, float(o), float(h), float(l), float(c), float(vol)))
    rows.sort(key=lambda r: r[0])
    return rows


def bucket_start(dt, tf_min):
    """Inizio del bucket per il timeframe dato (allineato a mezzanotte)."""
    if tf_min >= 1440:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes = dt.hour * 60 + dt.minute
    b = (minutes // tf_min) * tf_min
    return dt.replace(hour=b // 60, minute=b % 60, second=0, microsecond=0)


def resample(rows, tf_min):
    """Aggrega le barre M1 in OHLCV per il timeframe richiesto."""
    out = []
    cur_key = None
    o = h = l = c = v = None
    for dt, ro, rh, rl, rc, rv in rows:
        key = bucket_start(dt, tf_min)
        if key != cur_key:
            if cur_key is not None:
                out.append((cur_key, o, h, l, c, v))
            cur_key, o, h, l, c, v = key, ro, rh, rl, rc, rv
        else:
            h = max(h, rh)
            l = min(l, rl)
            c = rc
            v += rv
    if cur_key is not None:
        out.append((cur_key, o, h, l, c, v))
    return out


def write_mt4(bars, path):
    with open(path, "w", encoding="utf-8") as f:
        for dt, o, h, l, c, v in bars:
            f.write(f"{dt.strftime('%Y.%m.%d')},{dt.strftime('%H:%M')},"
                    f"{o:.3f},{h:.3f},{l:.3f},{c:.3f},{int(v)}\n")


def main():
    ap = argparse.ArgumentParser(description="Resample M1 HistData -> CSV MT4")
    ap.add_argument("pair")
    ap.add_argument("--tf", nargs="+", default=["M5", "M15", "M30", "H1", "H4", "D1"])
    ap.add_argument("--tz", type=int, default=0, help="shift orario in ore (es. 7 per EST->EET)")
    args = ap.parse_args()

    pair = args.pair.upper()
    paths = glob.glob(os.path.join(RAWDIR, f"DAT_ASCII_{pair}_M1_*.csv"))
    if not paths:
        print(f"Nessun M1 trovato per {pair} in {RAWDIR}. Lancia prima histdata_download.py")
        sys.exit(1)

    print(f"Leggo {len(paths)} file M1 di {pair} (tz shift {args.tz}h)...")
    rows = read_m1(paths, args.tz)
    print(f"Totale barre M1: {len(rows):,}  ({rows[0][0]} -> {rows[-1][0]})")

    os.makedirs(OUTDIR, exist_ok=True)
    for tf in args.tf:
        tf = tf.upper()
        if tf not in TF_MIN:
            print(f"  TF {tf} non supportato, salto")
            continue
        bars = rows if tf == "M1" else resample(rows, TF_MIN[tf])
        out = os.path.join(OUTDIR, f"{pair}_{tf}.csv")
        write_mt4(bars, out)
        print(f"  {tf:3s}: {len(bars):>8,} barre -> {os.path.relpath(out)}")


if __name__ == "__main__":
    main()
