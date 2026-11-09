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

tickers = ["IMOEX", "RGBI", "SBER", "SBERP", "VTBR", "T", "MBNK", "BSPB", "SVCB", "CBOM"]

with Client(token) as client:
    for ticker in tickers:
        found = client.instruments.find_instrument(query=ticker).instruments
        uid = ""
        for u in found:
            if u.ticker == ticker and u.class_code in ["TQBR", "SNDX"] or (u.ticker == ticker and uid == ""):
                uid = u.uid
                info = f"{u.ticker} {u.class_code} {u.name} first day {u.first_1day_candle_date} first min {u.first_1min_candle_date}"
        if uid == "":
            print(ticker, "not found")
            continue
        print(info)

        rows = []
        for year in range(2021, 2027):
            start = datetime(year, 1, 1, tzinfo=timezone.utc)
            end = datetime(year, 12, 31, 23, 59, tzinfo=timezone.utc)
            time.sleep(0.1)
            candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_DAY, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
            for c in candles:
                rows.append({"date": f"{c.time:%Y-%m-%d}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close), "volume": c.volume})
        df = pandas.DataFrame(rows)
        df.to_csv(f"data/daily/{ticker}.csv", index=False)
        print(f"   {len(df)} days, {df['date'][0] if len(df) > 0 else '-'} -> {df['date'][len(df) - 1] if len(df) > 0 else '-'}")
