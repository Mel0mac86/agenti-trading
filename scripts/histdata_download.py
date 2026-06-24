#!/usr/bin/env python3
"""
histdata_download.py - Scarica i dati storici M1 da HistData.com.

HistData fornisce barre da 1 minuto (M1) in formato ASCII. Da queste si
generano tutti gli altri timeframe con resample_mt4.py.

Uso:
    python3 histdata_download.py XAUUSD 2020 2021 2022 2023 2024
    python3 histdata_download.py XAUUSD 2024            # un solo anno
    python3 histdata_download.py EURUSD 2023 2024

Note:
    - Fuso orario dei dati: EST (UTC-5) senza ora legale. Tienine conto nel
      backtest (i broker MT4 sono di solito EET, UTC+2/+3): vedi --tz in resample.
    - Solo stdlib: funziona ovunque ci sia Python 3.
    - Materiale didattico; rispetta i termini d'uso di HistData.com.
"""
import sys, os, re, time, zipfile, urllib.request, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
BASE = "https://www.histdata.com"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")


def _req(url, data=None, referer=None):
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    body = urllib.parse.urlencode(data).encode() if data else None
    if body:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    return urllib.request.urlopen(urllib.request.Request(url, body, headers), timeout=60)


def download(pair, year, month=None):
    """Scarica un anno (o un mese) M1 e restituisce il path del CSV estratto."""
    pair_l = pair.lower()
    sub = f"{year}/{month}" if month else f"{year}"
    page = f"{BASE}/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{pair_l}/{sub}"
    html = _req(page).read().decode("utf-8", "ignore")

    m = re.search(r'name="tk"\s+id="tk"\s+value="([0-9a-f]+)"', html)
    if not m:
        raise RuntimeError(f"Token non trovato per {pair} {sub} (pagina cambiata o dati assenti)")
    tk = m.group(1)

    datemonth = f"{year}{int(month):02d}" if month else f"{year}"
    form = {"tk": tk, "date": str(year), "datemonth": datemonth,
            "platform": "ASCII", "timeframe": "M1", "fxpair": pair.upper()}
    zip_bytes = _req(f"{BASE}/get.php", data=form, referer=page).read()

    os.makedirs(OUTDIR, exist_ok=True)
    tag = f"{pair.upper()}_{datemonth}"
    zip_path = os.path.join(OUTDIR, f"{tag}.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    with zipfile.ZipFile(zip_path) as z:
        csv_name = next((n for n in z.namelist() if n.lower().endswith(".csv")), None)
        if not csv_name:
            raise RuntimeError(f"Nessun CSV nello zip {tag} (anno/mese non disponibile?)")
        z.extract(csv_name, OUTDIR)
    os.remove(zip_path)
    return os.path.join(OUTDIR, csv_name)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    pair, years = sys.argv[1], [int(y) for y in sys.argv[2:]]
    import datetime
    cur_year = datetime.datetime.utcnow().year
    cur_month = datetime.datetime.utcnow().month

    for y in years:
        try:
            if y == cur_year:
                # anno in corso: HistData lo serve mese per mese
                for mth in range(1, cur_month + 1):
                    try:
                        path = download(pair, y, mth)
                        print(f"OK  {pair} {y}-{mth:02d} -> {os.path.basename(path)}")
                    except Exception as e:
                        print(f"--  {pair} {y}-{mth:02d}: {e}")
                    time.sleep(1)
            else:
                path = download(pair, y)
                size = os.path.getsize(path)
                print(f"OK  {pair} {y} -> {os.path.basename(path)} ({size//1024} KB)")
        except Exception as e:
            print(f"ERR {pair} {y}: {e}")
        time.sleep(1)


if __name__ == "__main__":
    main()
