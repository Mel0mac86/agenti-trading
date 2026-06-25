#!/usr/bin/env python3
"""
grid_backtest.py - Simula una GRIGLIA (grid trading) long sui dati reali e ne
misura il vero profilo di rischio: il drawdown FLOTTANTE che si accumula quando
il prezzo va in trend contro la griglia (le posizioni restano aperte senza stop).

Griglia long classica: livelli ogni G sotto un riferimento. A ogni livello toccato
in discesa si apre un long; ogni long chiude in profitto a +G (take-profit). Nessuno
stop loss (è il punto della griglia... ed è il suo tallone d'Achille).

Metriche chiave:
  - profitto realizzato (somma dei +G incassati)
  - max drawdown FLOTTANTE (perdita non realizzata al picco di stress)
  - max livelli aperti contemporaneamente (= margine richiesto)
  - rapporto profitto/rischio: quanto guadagni vs quanto rischi di perdere in un colpo

Uso: python3 grid_backtest.py XAUUSD H1 --grid 5
     python3 grid_backtest.py EURUSD H1 --grid 0.0030
"""
import os, sys, argparse
from backtest import load, DATADIR

LOT = 1.0          # 1 unita' (1 oz oro / 1 micro-unita' forex)
MAX_LEVELS = 300   # oltre = margin call nella realta'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair"); ap.add_argument("tf")
    ap.add_argument("--grid", type=float, required=True, help="passo della griglia in prezzo")
    args = ap.parse_args()
    p = os.path.join(DATADIR, f"{args.pair.upper()}_{args.tf}.csv")
    if not os.path.exists(p):
        print(f"manca {p}"); return
    t, o, h, l, c = load(p)
    G = args.grid
    ref = c[0]

    open_levels = {}      # k -> entry price
    realized = 0.0
    max_float_dd = 0.0
    max_open = 0
    margin_call = False

    for i in range(len(c)):
        # chiusure in profitto: long al livello k chiude a entry+G
        for k in list(open_levels.keys()):
            if h[i] >= open_levels[k] + G:
                realized += G * LOT
                del open_levels[k]
        # aperture: ogni livello sotto il riferimento toccato in discesa
        k_max = int((ref - l[i]) / G)
        for k in range(1, k_max + 1):
            if k not in open_levels:
                if len(open_levels) >= MAX_LEVELS:
                    margin_call = True
                    break
                open_levels[k] = ref - k * G
        max_open = max(max_open, len(open_levels))
        # drawdown flottante corrente (posizioni aperte sotto il prezzo)
        if open_levels:
            floating = sum((c[i] - e) * LOT for e in open_levels.values())
            if floating < 0:
                max_float_dd = min(max_float_dd, floating)
        if margin_call:
            break

    print(f"# GRIGLIA long — {args.pair} {args.tf} | passo {G} | {t[0].date()} -> {t[i].date()}")
    print(f"  Profitto realizzato (lotto 1)    : {realized:,.1f} (prezzo)")
    print(f"  Max drawdown FLOTTANTE           : {max_float_dd:,.1f} (prezzo)")
    print(f"  Max livelli aperti insieme       : {max_open}")
    rr = realized / abs(max_float_dd) if max_float_dd < 0 else float('inf')
    print(f"  Rapporto profitto / rischio-picco: {rr:.2f}")
    if margin_call:
        print(f"  >>> MARGIN CALL: superati {MAX_LEVELS} livelli aperti = conto azzerato")
    # traduzione su conto da 100€ (esempio, lotto minimo realistico)
    print()
    print("  Lettura: il profitto si incassa a gocce; il rischio si accumula tutto")
    print("  insieme nel drawdown flottante. Se il flottante supera il tuo conto,")
    print("  margin call e azzeramento. La griglia 'vince spesso' e perde tutto in un colpo.")


if __name__ == "__main__":
    main()
