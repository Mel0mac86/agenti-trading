# Dati di mercato (HistData → MT4)

Questa cartella **non è versionata** (vedi `.gitignore`): i dati sono grandi e
si rigenerano in pochi minuti con gli script in [`../scripts`](../scripts).

## Generare i dati

```bash
# 1) Scarica le barre M1 da HistData (uno o più anni)
python3 scripts/histdata_download.py XAUUSD 2020 2021 2022 2023 2024
#    -> data/raw/DAT_ASCII_XAUUSD_M1_AAAA.csv

# 2) Genera i timeframe in formato importabile su MT4
python3 scripts/resample_mt4.py XAUUSD --tf M5 M15 M30 H1 H4 D1
#    -> data/mt4/XAUUSD_<TF>.csv
```

Funzionano anche altri simboli di HistData (es. `EURUSD`, `XAGUSD`, `GBPUSD`).

## Formato di output (MT4)

```
YYYY.MM.DD,HH:MM,Open,High,Low,Close,Volume
2024.01.01,18:00,2062.598,2066.595,2062.405,2063.615,0
```

## Importare in MetaTrader 4

1. MT4 → **Strumenti → History Center** (F2).
2. Seleziona il simbolo (es. XAUUSD) e il timeframe, poi **Import**.
3. Scegli il file `data/mt4/XAUUSD_<TF>.csv`, separatore **virgola**, e importa.
4. Per lo **Strategy Tester**: imposta spread reale (XAU/USD = **8 points**) e la
   commissione del broker; usa "Every tick" per la massima qualità.

## ⚠️ Fuso orario

I dati HistData sono in **EST (UTC-5)** fisso. I broker MT4 sono di solito **EET
(UTC+2/+3)**. Se vuoi allineare gli orari (rilevante per filtri di sessione e per
il confine dei daily), rigenera con uno shift:

```bash
python3 scripts/resample_mt4.py XAUUSD --tz 7    # EST -> EET
```

## Qualità del dato

- Il volume è "tick volume" (spesso 0 in alcune righe HistData): usalo solo come
  indicazione, non come volume reale scambiato.
- HistData è dati **aggregati retail**, ottimi per sviluppo e backtest; possono
  differire dai tick del tuo broker. La validazione finale va fatta sul **tuo**
  broker, in **demo**.
