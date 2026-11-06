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
changes = pandas.read_csv("data/cb_kir_decisions.csv")

nbh = [1, 3, 5, 10, 30, 60]

def get_price(x):
    return x.units + x.nano * 1e-9

with Client(token) as client:
    uid = "4821c9aa-36e8-4743-b37c-861e58581b25"
    data = []
    for day, tm, pc in zip(changes["date"], changes["time"], changes["press_conf"]):
        date = datetime.strptime(day, "%Y-%m-%d")
        start = date.replace(hour=6, tzinfo=timezone.utc)
        end = date.replace(hour=21, tzinfo=timezone.utc)
        candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE)
        data.append([])
        for i in candles.candles:
            data[-1].append({"time": i.time, "open": get_price(i.open), "close": get_price(i.close), "low": get_price(i.low), "high": get_price(i.high)})
        data[-1] = pandas.DataFrame(data[-1])
    out = open("data/results.txt", "w")
    for k in range(len(data)):
        day = changes["date"][k]
        df = data[k]
        rb = changes["rate_before"][k]
        ra = changes["rate_after"][k]
        out.write(f"{day} - {rb} -> {ra} ({ra - rb:+})\n")
        if len(df) == 0:
            out.write("No data available\n\n")
            continue
        opens = {}
        closes = {}
        for i in range(len(df)):
            t = df["time"][i]
            opens[t.hour * 60 + t.minute] = df["open"][i]
            closes[t.hour * 60 + t.minute] = df["close"][i]
        news = 10 * 60 + 30
        for x in nbh:
            a = news - x
            b = news + x - 1
            if a in opens and b in closes:
                change = (closes[b] - opens[a]) / opens[a] * 100
                out.write(f"+-{x} : {opens[a]:.5f} -> {closes[b]:.5f} : {change:+.5f}%\n")
            else:
                out.write(f"+-{x} : no candles\n")
        day_open = df["open"][0]
        day_close = df["close"][len(df) - 1]
        change = (day_close - day_open) / day_open * 100
        out.write(f"day : {day_open:.5f} -> {day_close:.5f} : {change:+.5f}%\n\n")
    out.close()
