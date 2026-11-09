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

def get_price(x):
    return x.units + x.nano * 1e-9

def pct(a, b):
    return (b - a) / a * 100

def corr(a, b):
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    c = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    return c / (va * vb) ** 0.5

idx = "4821c9aa-36e8-4743-b37c-861e58581b25"
rgbi = "fceffb27-3c51-4101-834c-d28c98ada458"
changes = pandas.read_csv("data/cb_kir_decisions.csv")
base = 10 * 60 + 29

with Client(token) as client:

    def minutes(uid, date):
        start = date.replace(hour=10, minute=0, tzinfo=timezone.utc)
        end = date.replace(hour=11, minute=40, tzinfo=timezone.utc)
        time.sleep(0.1)
        res = {}
        for c in client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
            res[c.time.hour * 60 + c.time.minute] = get_price(c.close)
        return res

    def daily(uid, date):
        start = (date - timedelta(days=14)).replace(tzinfo=timezone.utc)
        end = date.replace(hour=23, minute=59, tzinfo=timezone.utc)
        time.sleep(0.1)
        res = []
        for c in client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_DAY, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
            res.append([f"{c.time:%Y-%m-%d}", get_price(c.close)])
        return res

    out = open("results/pre_decision/raw/bonds.txt", "w")
    out.write("date        decision         |  RGBI week   +1     +5    +60  |  IMOEX +1    +5    +60   day\n")
    rows = []
    for k in range(len(changes)):
        day = changes["date"][k]
        if day < "2021-04-16":
            continue
        rb = changes["rate_before"][k]
        ra = changes["rate_after"][k]
        date = datetime.strptime(day, "%Y-%m-%d")
        b = minutes(rgbi, date)
        x = minutes(idx, date)
        bd = daily(rgbi, date)
        xd = daily(idx, date)
        if base not in b or base not in x or len(xd) < 2 or xd[-1][0] != day:
            out.write(f"{day}  no data\n")
            continue
        t = "hold"
        if ra > rb:
            t = "hike"
        if ra < rb:
            t = "cut"
        r = {"date": day, "type": t, "rb": rb, "ra": ra, "x_day": pct(xd[-2][1], xd[-1][1]), "b_week": None}
        if len(bd) >= 7 and bd[-1][0] == day:
            r["b_week"] = pct(bd[-7][1], bd[-2][1])
        for m in [1, 5, 60]:
            r[f"b{m}"] = pct(b[base], b[base + m]) if base + m in b else 0
            r[f"x{m}"] = pct(x[base], x[base + m]) if base + m in x else 0
        rows.append(r)
        bw = f"{r['b_week']:+6.2f}" if r["b_week"] is not None else "     -"
        out.write(f"{day}  {rb:5.2f} -> {ra:5.2f} {t:4} | {bw} {r['b1']:+6.2f} {r['b5']:+6.2f} {r['b60']:+6.2f} | {r['x1']:+6.2f} {r['x5']:+6.2f} {r['x60']:+6.2f} {r['x_day']:+6.2f}\n")

    n = len(rows)
    out.write(f"\ndecisions: {n}   (noise level for correlation: about +-{2 / n ** 0.5:.2f})\n")
    out.write("RGBI up = yields down = decision softer than expected\n\n")

    out.write("1. does the bond reaction explain the stock reaction?\n")
    old = [r for r in rows if r["date"] < "2023-07"]
    new = [r for r in rows if r["date"] >= "2023-07"]
    for name, part in [["all", rows], ["before jul 2023", old], ["from jul 2023", new]]:
        for a, c in [["b1", "x1"], ["b5", "x5"], ["b60", "x60"], ["b60", "x_day"]]:
            p = [r[a] for r in part]
            q = [r[c] for r in part]
            same = sum(1 for i in range(len(part)) if (p[i] > 0) == (q[i] > 0))
            out.write(f"   {name:16} {a:4} -> {c:5}  corr {corr(p, q):+.2f}   same sign {same}/{len(part)}\n")

    out.write("\n2. does the bond move in the week before tell where stocks go?\n")
    part = [r for r in rows if r["b_week"] is not None]
    for c in ["x1", "x60", "x_day"]:
        out.write(f"   b_week -> {c:5}  corr {corr([r['b_week'] for r in part], [r[c] for r in part]):+.2f}\n")

    out.write("\n3. cuts since 2025: was the decision a disappointment?\n")
    for r in rows:
        if r["type"] == "cut" and r["date"] >= "2025":
            out.write(f"   {r['date']}  {r['rb']:5.2f} -> {r['ra']:5.2f}   RGBI +5 {r['b5']:+.2f}%   IMOEX +5 {r['x5']:+.2f}%   IMOEX day {r['x_day']:+.2f}%\n")
    out.close()
