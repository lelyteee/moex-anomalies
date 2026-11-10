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

def pct(a, b):
    return (b - a) / a * 100

def corr(a, b):
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    c = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    return c / (va * vb) ** 0.5

def slope(x, y):
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    return sum((x[i] - mx) * (y[i] - my) for i in range(len(x))) / sum((v - mx) ** 2 for v in x)

tickers = ["SVCB", "MBNK", "CBOM", "ZAYM", "AVAN", "PRMB", "KUZB", "ROSB"]
changes = pandas.read_csv("data/cb_kir_decisions.csv")
base = 10 * 60 + 29

with Client(token) as client:
    names = []
    uids = []
    found = []
    for t in tickers:
        for u in client.instruments.find_instrument(query=t).instruments:
            if u.ticker == t and u.class_code == "TQBR":
                names.append(t)
                uids.append(u.uid)
                found.append({"ticker": t, "uid": u.uid, "name": u.name, "first_1min": u.first_1min_candle_date})
        time.sleep(0.1)
    pandas.DataFrame(found).to_csv("data/small_banks.csv", index=False)
    names += ["IMOEX", "RGBI"]
    uids += ["4821c9aa-36e8-4743-b37c-861e58581b25", "fceffb27-3c51-4101-834c-d28c98ada458"]

    rows = []
    for k in range(len(changes)):
        day = changes["date"][k]
        date = datetime.strptime(day, "%Y-%m-%d")
        start = date.replace(hour=10, minute=14, tzinfo=timezone.utc)
        end = date.replace(hour=11, minute=40, tzinfo=timezone.utc)
        r = {"date": day, "rb": changes["rate_before"][k], "ra": changes["rate_after"][k]}
        for j in range(len(names)):
            m = {}
            for c in client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uids[j], candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
                m[c.time.hour * 60 + c.time.minute] = [get_price(c.open), get_price(c.close), c.volume]
            time.sleep(0.1)
            before = [t for t in range(10 * 60 + 15, base) if t in m]
            after = [t for t in range(base + 1, base + 61) if t in m]
            if len(before) == 0 or len(after) == 0:
                continue
            p0 = m[before[-1]][1]
            p5 = m[[t for t in after if t <= base + 5][-1]][1] if after[0] <= base + 5 else p0
            p60 = m[after[-1]][1]
            pre = 0
            if base in m:
                pre = pct(m[base][0], m[base][1])
            r[names[j]] = {"pre": pre, "x5": pct(p0, p5), "x60": pct(p0, p60), "trades": len(before) + len(after) + (1 if base in m else 0)}
            if base in m:
                r[names[j]]["x5"] = pct(m[base][1], p5)
                r[names[j]]["x60"] = pct(m[base][1], p60)
        rows.append(r)

out = open("results/pre_decision/raw/small_banks.txt", "w")
out.write("move from the last price before 10:30 UTC, pre = move inside 10:29, min = minutes with trades in 10:15-11:29 (out of 75)\n\n")
out.write("date        decision      |" + "".join(f" {s:>18} |" for s in names[:-1]) + "\n")
out.write("                          |" + "   +5   +60   min |" * (len(names) - 1) + "\n")
for r in rows:
    line = f"{r['date']}  {r['rb']:5.2f}->{r['ra']:5.2f} |"
    for s in names[:-1]:
        if s in r:
            line += f" {r[s]['x5']:+5.2f} {r[s]['x60']:+5.2f} {r[s]['trades']:4} |"
        else:
            line += "          -         |"
    out.write(line + "\n")

new = [r for r in rows if r["date"] >= "2023-07"]
out.write("\nfrom jul 2023, +60 min\n")
out.write("stock   n   | minutes with trades | per 1% of IMOEX | per 1% of RGBI | corr with RGBI | mean |+60|\n")
for s in names[:-1]:
    part = [r for r in new if s in r and "IMOEX" in r and "RGBI" in r]
    if len(part) < 5:
        out.write(f"{s:6} {len(part):3}   | too few days\n")
        continue
    x = [r[s]["x60"] for r in part]
    ix = [r["IMOEX"]["x60"] for r in part]
    b = [r["RGBI"]["x60"] for r in part]
    tr = sum(r[s]["trades"] for r in part) / len(part)
    a60 = sum(abs(v) for v in x) / len(x)
    out.write(f"{s:6} {len(part):3}   |        {tr:4.0f}         |      {slope(ix, x):+5.2f}      |     {slope(b, x):+6.2f}     |     {corr(b, x):+.2f}      |   {a60:.2f}%\n")

out.write("\nbefore the release: |pre| >= 0.5% in the minute 10:29\n")
for s in names[:-2]:
    part = [r for r in rows if s in r]
    hits = [r for r in part if abs(r[s]["pre"]) >= 0.5]
    same = sum(1 for r in hits if (r[s]["pre"] > 0) == (r[s]["x5"] > 0))
    out.write(f"{s:6} days {len(part):2}   big pre moves {len(hits)}   same direction as +5: {same}\n")
    for r in hits:
        out.write(f"       {r['date']}  {r['rb']:5.2f}->{r['ra']:5.2f}   pre {r[s]['pre']:+.2f}%   +5 {r[s]['x5']:+.2f}%   +60 {r[s]['x60']:+.2f}%\n")
out.close()
