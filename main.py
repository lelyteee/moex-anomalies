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
    out = open("results/results_2.txt", "w")
    raw = open("results/around_1030.txt", "w")
    for k in range(len(data)):
        day = changes["date"][k]
        df = data[k]
        rb = changes["rate_before"][k]
        ra = changes["rate_after"][k]
        out.write(f"{day} - {rb} -> {ra} ({ra - rb:+})\n")
        raw.write(f"{day}\n")
        if len(df) == 0:
            out.write("No data available\n\n")
            raw.write("No data available\n\n")
            continue
        opens = {}
        closes = {}
        for i in range(len(df)):
            t = df["time"][i]
            m = t.hour * 60 + t.minute
            opens[m] = df["open"][i]
            closes[m] = df["close"][i]
            if 10 * 60 + 25 <= m <= 10 * 60 + 35:
                raw.write(f"{t.hour:02}:{t.minute:02}  o {df['open'][i]:.2f}  h {df['high'][i]:.2f}  l {df['low'][i]:.2f}  c {df['close'][i]:.2f}\n")
        raw.write("\n")
        base_time = 10 * 60 + 29
        if base_time not in closes:
            out.write("No 10:29 candle\n\n")
            continue
        base = closes[base_time]
        pre = (base - opens[base_time]) / opens[base_time] * 100
        out.write(f"10:29 : {opens[base_time]:.2f} -> {base:.2f} : {pre:+.2f}%\n")
        for x in nbh:
            b = base_time + x
            if b in closes:
                change = (closes[b] - base) / base * 100
                out.write(f"+{x} : {base:.2f} -> {closes[b]:.2f} : {change:+.2f}%\n")
            else:
                out.write(f"+{x} : no candles\n")
        day_close = df["close"][len(df) - 1]
        change = (day_close - base) / base * 100
        out.write(f"to close : {base:.2f} -> {day_close:.2f} : {change:+.2f}%\n\n")
    out.close()
    raw.close()
