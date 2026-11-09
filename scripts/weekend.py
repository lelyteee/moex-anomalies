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

idx = "4821c9aa-36e8-4743-b37c-861e58581b25"
ix2 = "83ef5122-e41e-4cf4-bbe4-b11a2b3f953e"

with Client(token) as client:

    def day_candles(uid, date):
        start = date.replace(hour=0, minute=0, tzinfo=timezone.utc)
        end = date.replace(hour=23, minute=59, tzinfo=timezone.utc)
        time.sleep(0.05)
        return client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles

    out = open("results/weekend/raw/weekend.txt", "w")
    out.write("saturday    sat  sun |  weekend      gap   monday\n")
    res = []
    sat = datetime(2026, 11, 7)
    for w in range(100):
        fri = day_candles(ix2, sat - timedelta(days=1))
        sa = day_candles(ix2, sat)
        su = day_candles(ix2, sat + timedelta(days=1))
        mon = day_candles(idx, sat + timedelta(days=2))
        line = f"{sat:%Y-%m-%d} {len(sa):4} {len(su):4} |"
        sat = sat - timedelta(days=7)
        if len(sa) + len(su) == 0 or len(fri) == 0 or len(mon) == 0:
            out.write(line + "  no weekend trading or no monday\n")
            continue
        fri_close = get_price(fri[-1].close)
        sun_close = get_price((su if len(su) > 0 else sa)[-1].close)
        mon_open = get_price(mon[0].open)
        mon_close = get_price(mon[-1].close)
        weekend = pct(fri_close, sun_close)
        gap = pct(sun_close, mon_open)
        monday = pct(mon_open, mon_close)
        res.append([weekend, gap, monday])
        out.write(line + f" {weekend:+7.2f}% {gap:+7.2f}% {monday:+7.2f}%\n")

    n = len(res)
    same = sum(1 for r in res if (r[0] > 0) == (r[2] > 0))
    up = [r[2] for r in res if r[0] > 0]
    down = [r[2] for r in res if r[0] <= 0]
    out.write(f"\nweekends with trading: {n}\n")
    out.write(f"monday goes the same way as the weekend: {same}/{n}\n")
    out.write(f"weekend up   ({len(up)}): mean monday {sum(up) / len(up):+.2f}%\n")
    out.write(f"weekend down ({len(down)}): mean monday {sum(down) / len(down):+.2f}%\n")
    out.close()
