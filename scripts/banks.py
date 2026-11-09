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

changes = pandas.read_csv("data/cb_kir_decisions.csv")
stocks = pandas.read_csv("data/banks.csv")
names = list(stocks["ticker"]) + ["IMOEX", "RGBI"]
uids = list(stocks["uid"]) + ["4821c9aa-36e8-4743-b37c-861e58581b25", "fceffb27-3c51-4101-834c-d28c98ada458"]
base = 10 * 60 + 29

with Client(token) as client:
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
            if base not in m or base + 60 not in m:
                continue
            normal = [m[t][2] for t in range(10 * 60 + 15, 10 * 60 + 25) if t in m]
            vx = 0
            if len(normal) > 0 and sum(normal) > 0:
                vx = m[base][2] / (sum(normal) / len(normal))
            r[names[j]] = {"pre": pct(m[base][0], m[base][1]), "vx": vx,
                           "x1": pct(m[base][1], m[base + 1][1]) if base + 1 in m else 0,
                           "x5": pct(m[base][1], m[base + 5][1]) if base + 5 in m else 0,
                           "x60": pct(m[base][1], m[base + 60][1])}
        rows.append(r)

out = open("results/pre_decision/raw/banks.txt", "w")
out.write("+1 / +60 = move from close 10:29 UTC, pre = move inside 10:29, vol = volume at 10:29 / mean 10:15-10:24\n\n")
out.write("date        decision      |" + "".join(f" {s:>17} |" for s in names) + "\n")
out.write("                          |" + "   +1   +60   pre |" * len(names) + "\n")
for r in rows:
    line = f"{r['date']}  {r['rb']:5.2f}->{r['ra']:5.2f} |"
    for s in names:
        if s in r:
            line += f" {r[s]['x1']:+5.2f} {r[s]['x60']:+5.2f} {r[s]['pre']:+5.2f} |"
        else:
            line += "         -         |"
    out.write(line + "\n")

new = [r for r in rows if r["date"] >= "2023-07"]
out.write("\nfrom jul 2023, sensitivity at +60 min\n")
out.write("stock   n   | per 1% of IMOEX | per 1% of RGBI | corr with RGBI | mean |+1| | +1 share of +60\n")
for s in names[:-1]:
    part = [r for r in new if s in r and "IMOEX" in r and "RGBI" in r]
    x = [r[s]["x60"] for r in part]
    ix = [r["IMOEX"]["x60"] for r in part]
    b = [r["RGBI"]["x60"] for r in part]
    a1 = sum(abs(r[s]["x1"]) for r in part) / len(part)
    a60 = sum(abs(r[s]["x60"]) for r in part) / len(part)
    out.write(f"{s:6} {len(part):3}   |      {slope(ix, x):+5.2f}      |     {slope(b, x):+6.2f}     |     {corr(b, x):+.2f}      |  {a1:.2f}%   |   {a1 / a60:.2f}\n")

out.write("\nfrom jul 2023, bank minus IMOEX from +5 to +60, traded in the direction of the RGBI +60 surprise\n")
for s in names[:-2]:
    part = [r for r in new if s in r and "IMOEX" in r and "RGBI" in r]
    pnl = []
    for r in part:
        rel = (r[s]["x60"] - r[s]["x5"]) - (r["IMOEX"]["x60"] - r["IMOEX"]["x5"])
        if r["RGBI"]["x60"] > 0:
            pnl.append(rel)
        else:
            pnl.append(-rel)
    out.write(f"   {s:6} n {len(pnl):2}   mean {sum(pnl) / len(pnl):+.3f}%   wins {sum(1 for p in pnl if p > 0)}/{len(pnl)}\n")

out.write("\nunusual minute 10:29 (before the release): |pre| > 3x the stock's median |pre| or volume > 10x\n")
for s in names[:-1]:
    part = [r for r in rows if s in r]
    med = sorted(abs(r[s]["pre"]) for r in part)[len(part) // 2]
    hits = [r for r in part if (abs(r[s]["pre"]) > 3 * med and abs(r[s]["pre"]) >= 0.1) or r[s]["vx"] > 10]
    same = sum(1 for r in hits if (r[s]["pre"] > 0) == (r[s]["x5"] > 0) and abs(r[s]["pre"]) >= 0.1)
    out.write(f"{s:6} median |pre| {med:.3f}%   unusual {len(hits)}/{len(part)}   same direction as +5 reaction: {same}\n")
    for r in hits:
        out.write(f"       {r['date']}  {r['rb']:5.2f}->{r['ra']:5.2f}   pre {r[s]['pre']:+.2f}%   vol x{r[s]['vx']:.1f}   +5 {r[s]['x5']:+.2f}%\n")
out.close()
