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

def corr(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    c = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    return c / (va * vb) ** 0.5

idx = "4821c9aa-36e8-4743-b37c-861e58581b25"
ix2 = "83ef5122-e41e-4cf4-bbe4-b11a2b3f953e"

with Client(token) as client:

    def day_candles(uid, date):
        start = date.replace(hour=0, minute=0, tzinfo=timezone.utc)
        end = date.replace(hour=23, minute=59, tzinfo=timezone.utc)
        time.sleep(0.05)
        return client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles

    def close_before(cs, h, m):
        res = -1
        for c in cs:
            if c.time.hour * 60 + c.time.minute < h * 60 + m:
                res = get_price(c.close)
        return res

    out = open("results/weekend/raw/weekend_gap.txt", "w")
    out.write("saturday   |  weekend    sat    sun | night  morning | to 10:05 | monday from 10:05\n")
    rows = []
    sat = datetime(2026, 11, 7)
    while sat >= datetime(2025, 6, 28):
        fri = day_candles(ix2, sat - timedelta(days=1))
        sa = day_candles(ix2, sat)
        su = day_candles(ix2, sat + timedelta(days=1))
        mo2 = day_candles(ix2, sat + timedelta(days=2))
        mo = day_candles(idx, sat + timedelta(days=2))
        line = f"{sat:%Y-%m-%d} |"
        d = f"{sat:%Y-%m-%d}"
        sat = sat - timedelta(days=7)
        if len(sa) < 500 or len(su) < 500 or len(fri) == 0 or len(mo2) == 0 or len(mo) == 0:
            out.write(line + " skipped\n")
            continue
        fri_close = get_price(fri[-1].close)
        sun_close = get_price(su[-1].close)
        mon_open2 = get_price(mo2[0].open)
        mon_morning = close_before(mo2, 6, 50)
        mon_1005 = close_before(mo, 7, 6)
        mon_close = get_price(mo[-1].close)
        r = {
            "date": d,
            "weekend": pct(fri_close, sun_close),
            "sat": pct(get_price(sa[0].open), get_price(sa[-1].close)),
            "sun": pct(get_price(su[0].open), sun_close),
            "night": pct(sun_close, mon_open2),
            "morning": pct(mon_open2, mon_morning),
            "to1005": pct(sun_close, mon_1005),
            "monday": pct(mon_1005, mon_close),
        }
        rows.append(r)
        out.write(line + f" {r['weekend']:+6.2f} {r['sat']:+6.2f} {r['sun']:+6.2f} | {r['night']:+5.2f} {r['morning']:+6.2f}  | {r['to1005']:+6.2f}   | {r['monday']:+6.2f}\n")

    n = len(rows)
    out.write(f"\nweekends: {n}   (noise level for correlation: about +-{2 / n ** 0.5:.2f})\n\n")
    pairs = [["sat", "sun"], ["weekend", "night"], ["weekend", "morning"], ["weekend", "to1005"], ["weekend", "monday"],
             ["night", "morning"], ["morning", "monday"], ["to1005", "monday"], ["sun", "monday"]]
    for a, b in pairs:
        x = [r[a] for r in rows]
        y = [r[b] for r in rows]
        same = sum(1 for i in range(n) if (x[i] > 0) == (y[i] > 0))
        up = [y[i] for i in range(n) if x[i] > 0]
        dn = [y[i] for i in range(n) if x[i] <= 0]
        out.write(f"{a:>8} -> {b:<8} corr {corr(x, y):+.2f}   same sign {same}/{n}   after up ({len(up)}): {sum(up) / len(up):+.2f}%   after down ({len(dn)}): {sum(dn) / len(dn):+.2f}%\n")

    out.write("\nmeans:\n")
    for k in ["weekend", "sat", "sun", "night", "morning", "to1005", "monday"]:
        v = [r[k] for r in rows]
        m = sum(v) / n
        sd = (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5
        ups = sum(1 for x in v if x > 0)
        out.write(f"{k:>8}: mean {m:+.3f}%   sd {sd:.2f}   up {ups}/{n}   t {m / (sd / n ** 0.5):+.1f}\n")
    out.close()
