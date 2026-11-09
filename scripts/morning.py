from t_tech.invest import Client
from t_tech.invest import CandleInterval
from datetime import datetime, timezone, timedelta
from t_tech.invest.schemas import CandleSource
import time

import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

def get_price(x):
    return x.units + x.nano * 1e-9

def pct(a, b):
    return (b - a) / a * 100

fut = "5bcff194-f10d-4314-b9ee-56b7fdb344fd"
ix2 = "83ef5122-e41e-4cf4-bbe4-b11a2b3f953e"

with Client(token) as client:

    def candles(uid, date):
        start = date.replace(hour=4, minute=0, tzinfo=timezone.utc)
        end = date.replace(hour=6, minute=50, tzinfo=timezone.utc)
        time.sleep(0.1)
        return client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles

    def price_at(cs, t):
        res = -1
        for c in cs:
            if c.time <= t:
                res = get_price(c.close)
        return res

    out = open("results/weekend/raw/morning.txt", "w")
    out.write("date        day | start | IMOEXF morning | IMOEX2 same window\n")
    names = ["mon", "tue", "wed", "thu", "fri"]
    res = {d: [] for d in names}
    starts = []
    date = datetime(2025, 8, 18)
    while date <= datetime(2026, 11, 9):
        day = names[date.weekday()] if date.weekday() < 5 else ""
        d = date
        date = date + timedelta(days=1)
        if day == "":
            continue
        f = candles(fut, d)
        x = candles(ix2, d)
        if len(f) < 10 or len(x) < 10:
            out.write(f"{d:%Y-%m-%d} {day} | no data\n")
            continue
        t0 = f[0].time
        t1 = f[-1].time
        x_open = price_at(x, t0)
        if x_open == -1:
            x_open = get_price(x[0].open)
        fm = pct(get_price(f[0].open), get_price(f[-1].close))
        xm = pct(x_open, price_at(x, t1))
        res[day].append([fm, xm])
        starts.append(f"{t0.hour:02}:{t0.minute:02}")
        out.write(f"{d:%Y-%m-%d} {day} | {t0.hour:02}:{t0.minute:02} | {fm:+7.2f}%       | {xm:+7.2f}%\n")

    out.write("\nfirst IMOEXF candle of the morning (UTC): ")
    for s in sorted(set(starts)):
        out.write(f"{s} x{starts.count(s)}  ")
    out.write("\n\nday   n  | IMOEXF: mean     up   t   | IMOEX2: mean     up   t\n")
    res["tue-fri"] = res["tue"] + res["wed"] + res["thu"] + res["fri"]
    for day in names + ["tue-fri"]:
        v = res[day]
        n = len(v)
        s = f"{day:7} {n:3} |"
        for j in [0, 1]:
            a = [r[j] for r in v]
            m = sum(a) / n
            sd = (sum((y - m) ** 2 for y in a) / (n - 1)) ** 0.5
            up = sum(1 for y in a if y > 0)
            s += f"  {m:+.3f}%  {up:3}/{n}  {m / (sd / n ** 0.5):+.1f}  |"
        out.write(s + "\n")
    out.close()
