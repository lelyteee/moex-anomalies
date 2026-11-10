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

def mean_abs(v):
    return sum(abs(x) for x in v) / len(v)

idx = "4821c9aa-36e8-4743-b37c-861e58581b25"
rgbi = "fceffb27-3c51-4101-834c-d28c98ada458"
changes = pandas.read_csv("data/cb_kir_decisions.csv")
points = [["release", 10, 29], ["+60", 11, 29], ["pre", 11, 59], ["12:30", 12, 30], ["13:00", 13, 0], ["close", 15, 49]]

with Client(token) as client:

    def day_prices(uid, date):
        start = date.replace(hour=10, minute=0, tzinfo=timezone.utc)
        end = date.replace(hour=16, minute=0, tzinfo=timezone.utc)
        time.sleep(0.1)
        cs = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        res = {}
        for name, h, m in points:
            for c in cs:
                if c.time.hour * 60 + c.time.minute <= h * 60 + m:
                    res[name] = get_price(c.close)
        return res

    def moves(p):
        return {"hour": pct(p["release"], p["+60"]), "gap": pct(p["+60"], p["pre"]),
                "press30": pct(p["pre"], p["12:30"]), "press60": pct(p["pre"], p["13:00"]),
                "after": pct(p["13:00"], p["close"]), "rest": pct(p["+60"], p["close"])}

    out = open("results/pre_decision/raw/press.txt", "w")
    out.write("IMOEX, UTC. hour = 10:29->11:29, gap = 11:29->11:59, press30 = 11:59->12:30, press60 = 11:59->13:00, after = 13:00->close\n")
    out.write("control = same times one week earlier\n\n")
    out.write("date        decision         | hour    gap  press30 press60  after |  RGBI press60 | control: gap press30 press60\n")
    rows = []
    for k in range(len(changes)):
        day = changes["date"][k]
        if day < "2021-04-16":
            continue
        date = datetime.strptime(day, "%Y-%m-%d")
        x = day_prices(idx, date)
        b = day_prices(rgbi, date)
        c = day_prices(idx, date - timedelta(days=7))
        if len(x) < 6 or len(b) < 6:
            out.write(f"{day}  no data\n")
            continue
        r = moves(x)
        r["date"] = day
        r["b_press60"] = pct(b["pre"], b["13:00"])
        r["b_hour"] = pct(b["release"], b["+60"])
        r["control"] = moves(c) if len(c) == 6 else None
        rows.append(r)
        cc = "   -      -      -"
        if r["control"] is not None:
            cc = f"{r['control']['gap']:+6.2f} {r['control']['press30']:+6.2f} {r['control']['press60']:+6.2f}"
        out.write(f"{day}  {changes['rate_before'][k]:5.2f} -> {changes['rate_after'][k]:5.2f}      | {r['hour']:+5.2f} {r['gap']:+6.2f} {r['press30']:+6.2f} {r['press60']:+6.2f} {r['after']:+6.2f} |     {r['b_press60']:+6.2f}    | {cc}\n")

    for name, part in [["before jul 2023", [r for r in rows if r["date"] < "2023-07"]], ["from jul 2023", [r for r in rows if r["date"] >= "2023-07"]]]:
        n = len(part)
        ctrl = [r["control"] for r in part if r["control"] is not None]
        out.write(f"\n{name}: {n} decisions, {len(ctrl)} controls   (noise for correlation about +-{2 / n ** 0.5:.2f})\n")
        out.write("1. how big is the move around the press conference?\n")
        for key in ["gap", "press30", "press60", "after"]:
            out.write(f"   {key:8} decision day mean |move| {mean_abs([r[key] for r in part]):.2f}%   control {mean_abs([c[key] for c in ctrl]):.2f}%\n")
        out.write("2. links\n")
        for a, b in [["hour", "press60"], ["b_press60", "press60"], ["press60", "rest"], ["b_hour", "press60"]]:
            p = [r[a] for r in part]
            q = [r[b] for r in part]
            same = sum(1 for i in range(n) if (p[i] > 0) == (q[i] > 0))
            out.write(f"   {a:9} -> {b:8} corr {corr(p, q):+.2f}   same sign {same}/{n}\n")
        p60 = [r["press60"] for r in part]
        rest = [r["rest"] for r in part]
        out.write(f"3. share of the move after the first hour that comes from 11:59-13:00: corr^2 = {corr(p60, rest) ** 2:.2f}\n")
    out.close()
