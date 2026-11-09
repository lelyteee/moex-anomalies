from t_tech.invest import Client
from t_tech.invest import CandleInterval
from datetime import datetime, timezone
from t_tech.invest.schemas import CandleSource
import time
import pandas

import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

def get_price(x):
    return x.units + x.nano * 1e-9

idx = "4821c9aa-36e8-4743-b37c-861e58581b25"
banks = ["SBER", "VTBR", "T", "BSPB", "LKOH"]

with Client(token) as client:
    rows = []
    for year in range(2021, 2027):
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year, 12, 31, 23, 59, tzinfo=timezone.utc)
        candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_DAY, instrument_id=idx, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        for c in candles:
            rows.append({"date": f"{c.time:%Y-%m-%d}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close)})
        time.sleep(0.1)
    pandas.DataFrame(rows).to_csv("data/imoex_daily.csv", index=False)

    out = open("results/pre_decision/raw/instruments.txt", "w")
    out.write(f"IMOEX daily: {len(rows)} days, {rows[0]['date']} -> {rows[-1]['date']}\n\n")
    for q in ["RGBI", "RGBITR"]:
        for u in client.instruments.find_instrument(query=q).instruments:
            out.write(f"{u.ticker} {u.class_code} {u.instrument_type} {u.uid} {u.first_1min_candle_date} {u.first_1day_candle_date} {u.name}\n")
    out.write("\n")

    found = []
    for b in banks:
        for u in client.instruments.find_instrument(query=b).instruments:
            if u.ticker == b and u.class_code == "TQBR":
                found.append({"ticker": b, "uid": u.uid, "name": u.name, "first_1min": u.first_1min_candle_date})
                out.write(f"{b} {u.uid} {u.first_1min_candle_date} {u.name}\n")
        time.sleep(0.1)
    pandas.DataFrame(found).to_csv("data/banks.csv", index=False)
    out.close()
