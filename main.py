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

with Client(token) as client:
    uid = "4821c9aa-36e8-4743-b37c-861e58581b25"
    start = datetime(2024, 10, 25, 9, 00, tzinfo=timezone.utc)
    end = datetime(2024, 10, 25, 11, 45, tzinfo=timezone.utc)
    candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid)
    rows = []
    for candle in candles.candles:
        row = {"time": candle.time, "open": get_price(candle.open), "high": get_price(candle.high), "low": get_price(candle.low),
               "close": get_price(candle.close), "volume": candle.volume}
        rows.append(row)
    df = pandas.DataFrame(rows)
    print(df)
    df.to_csv("data/imoex_2024-10-25.csv", index=False)