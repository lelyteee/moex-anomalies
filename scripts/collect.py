# Saves raw 5-second candles (open, high, low, close, volume) for whole days.
# T-Invest keeps 5-second candles only for about 30 days: run this at least every 3 weeks,
# and within a few days after every decision.
# Output: data/seconds/DATE_TICKER.csv, and data/seconds/log.txt with what was saved.

from t_tech.invest import Client
from t_tech.invest import CandleInterval
from datetime import datetime, timezone, timedelta
from t_tech.invest.schemas import CandleSource
import time
import pandas

import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

# every weekday of the last 29 days (older ones are already gone); days already saved are skipped
dates = []
for i in range(1, 30):
    d = datetime.now(timezone.utc) - timedelta(days=i)
    if d.weekday() < 5:
        dates.append(f"{d:%Y-%m-%d}")


def get_price(x):
    return x.units + x.nano * 1e-9


instruments = pandas.read_csv("data/instruments.csv", dtype=str).fillna("")
os.makedirs("data/seconds", exist_ok=True)
log = open("data/seconds/log.txt", "a")

with Client(token) as client:
    # futures without a uid in the file: find it by ticker
    for k in range(len(instruments)):
        if instruments["uid"][k] == "":
            for u in client.instruments.find_instrument(query=instruments["ticker"][k]).instruments:
                if u.ticker == instruments["ticker"][k]:
                    instruments.loc[k, "uid"] = u.uid
                    break
    instruments.to_csv("data/instruments.csv", index=False)

    for day in dates:
        d = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        for k in range(len(instruments)):
            ticker = instruments["ticker"][k]
            if os.path.exists(f"data/seconds/{day}_{ticker}.csv"):
                continue
            rows = []
            error = ""
            # one request can cover only a few hours of 5-second candles, so go in 2-hour pieces
            for h in range(0, 24, 2):
                start = d + timedelta(hours=h)
                try:
                    candles = client.market_data.get_candles(from_=start, to=start + timedelta(hours=2), interval=CandleInterval.CANDLE_INTERVAL_5_SEC, instrument_id=instruments["uid"][k], candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
                except Exception as e:
                    error = str(e)[:120]
                    break
                for c in candles:
                    rows.append({"time": c.time, "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close), "volume": c.volume})
                time.sleep(0.1)
            if len(rows) > 0:
                pandas.DataFrame(rows).drop_duplicates("time").to_csv(f"data/seconds/{day}_{ticker}.csv", index=False)
            log.write(f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M}  {day}  {ticker:7} {len(rows):6} candles  {error}\n")
log.close()
