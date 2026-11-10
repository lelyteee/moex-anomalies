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

steps = ["daily", "extra", "week", "bonds", "drift", "banks", "small_banks", "press"]

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


def step_daily():
    idx = "4821c9aa-36e8-4743-b37c-861e58581b25"
    banks = ["SBER", "VTBR", "T", "BSPB", "LKOH"]

    with Client(token) as client:
        rows = []
        for year in range(2021, 2027):
            start = datetime(year, 1, 1, tzinfo=timezone.utc)
            end = datetime(year, 12, 31, 23, 59, tzinfo=timezone.utc)
            candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_DAY, instrument_id=idx, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
            for c in candles:
                rows.append({"date": f"{c.time:%Y-%m-%d}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close)})
            time.sleep(0.1)
        pandas.DataFrame(rows).to_csv("data/imoex_daily.csv", index=False)

        out = open("results/pre_decision/raw/instruments.txt", "w")
        out.write(f"IMOEX daily: {len(rows)} days, {rows[0]['date']} -> {rows[-1]['date']}\n\n")
        for q in ["RGBI", "RGBITR"]:
            for u in client.instruments.find_instrument(query=q).instruments:
                out.write(f"{u.ticker} {u.class_code} {u.instrument_type} {u.uid} {u.first_1min_candle_date} {u.first_1day_candle_date} {u.name}\n")
        out.write("\n")

        found = []
        for b in banks:
            for u in client.instruments.find_instrument(query=b).instruments:
                if u.ticker == b and u.class_code == "TQBR":
                    found.append({"ticker": b, "uid": u.uid, "name": u.name, "first_1min": u.first_1min_candle_date})
                    out.write(f"{b} {u.uid} {u.first_1min_candle_date} {u.name}\n")
            time.sleep(0.1)
        pandas.DataFrame(found).to_csv("data/banks.csv", index=False)
        out.close()


def step_extra():
    extra = [
        ["2022-04-08", 8, 40, 20.0, 17.0],
        ["2022-05-26", 7, 30, 14.0, 11.0],
        ["2023-08-15", 7, 30, 8.5, 12.0],
    ]

    with Client(token) as client:
        uid = "4821c9aa-36e8-4743-b37c-861e58581b25"
        for day, h, m, rb, ra in extra:
            date = datetime.strptime(day, "%Y-%m-%d")
            news = date.replace(hour=h, minute=m, tzinfo=timezone.utc)
            start = news - timedelta(minutes=16)
            end = news + timedelta(minutes=46)
            candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
            print(f"{day}   {rb} -> {ra} ({ra - rb:+})   release {h:02}:{m:02} UTC   ({len(candles)} candles)")
            print("time  |    open    close      %")
            prev = -1
            for c in candles:
                t = c.time
                o = get_price(c.open)
                cl = get_price(c.close)
                if prev == -1:
                    prev = o
                p = (cl - prev) / prev * 100
                prev = cl
                mark = "  <- release" if t == news else ""
                print(f"{t.hour:02}:{t.minute:02} | {o:8.2f} {cl:8.2f} {p:+6.2f}%{mark}")
            print()


def step_week():
    def stats(v):
        n = len(v)
        m = sum(v) / n
        sd = (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5
        up = sum(1 for x in v if x > 0)
        return f"n {n:4}   mean {m:+.3f}%   up {up}/{n}   t {m / (sd / n ** 0.5):+.1f}"

    daily = pandas.read_csv("data/imoex_daily.csv")
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    dates = list(daily["date"])
    close = list(daily["close"])

    react = {}
    for b in open("results/key_rate/raw/results_2.txt").read().strip().split("\n\n"):
        lines = b.split("\n")
        react[lines[0].split()[0]] = {}
        for l in lines[1:]:
            if l.startswith("+1 ") or l.startswith("+60 "):
                react[lines[0].split()[0]][l.split()[0]] = float(l.split(" : ")[-1].rstrip("%"))

    out = open("results/pre_decision/raw/index_week.txt", "w")
    out.write("date        decision         | week before  day before | decision day | +1 min  +60 min\n")
    rows = []
    for k in range(len(changes)):
        day = changes["date"][k]
        rb = changes["rate_before"][k]
        ra = changes["rate_after"][k]
        if day not in dates or "+1" not in react.get(day, {}):
            continue
        i = dates.index(day)
        t = "hold"
        if ra > rb:
            t = "hike"
        if ra < rb:
            t = "cut"
        r = {"date": day, "type": t, "week": pct(close[i - 6], close[i - 1]), "prev": pct(close[i - 2], close[i - 1]),
             "day": pct(close[i - 1], close[i]), "m1": react[day]["+1"], "m60": react[day]["+60"]}
        rows.append(r)
        out.write(f"{day}  {rb:5.2f} -> {ra:5.2f} {t:4} | {r['week']:+8.2f}%  {r['prev']:+8.2f}%  | {r['day']:+8.2f}%    | {r['m1']:+6.2f}  {r['m60']:+6.2f}\n")

    n = len(rows)
    out.write(f"\ndecisions: {n}   (noise level for correlation: about +-{2 / n ** 0.5:.2f})\n\n")

    out.write("1. does the week before tell anything about the reaction?\n")
    for a, b in [["week", "m1"], ["week", "m60"], ["week", "day"], ["prev", "m1"], ["prev", "day"]]:
        x = [r[a] for r in rows]
        y = [r[b] for r in rows]
        same = sum(1 for i in range(n) if (x[i] > 0) == (y[i] > 0))
        out.write(f"   {a:5} -> {b:4}  corr {corr(x, y):+.2f}   same sign {same}/{n}\n")
    old = [r for r in rows if r["date"] < "2023-07"]
    new = [r for r in rows if r["date"] >= "2023-07"]
    out.write(f"   before jul 2023  week -> m1  corr {corr([r['week'] for r in old], [r['m1'] for r in old]):+.2f}   n {len(old)}\n")
    out.write(f"   from jul 2023    week -> m1  corr {corr([r['week'] for r in new], [r['m1'] for r in new]):+.2f}   n {len(new)}\n")

    out.write("\n2. is the week before a decision different from a normal week?\n")
    dec = [r["date"] for r in rows]
    weeks = []
    days = []
    for i in range(6, len(dates)):
        if dates[i] not in dec:
            weeks.append(pct(close[i - 6], close[i - 1]))
            days.append(pct(close[i - 2], close[i - 1]))
    out.write(f"   week before decision: {stats([r['week'] for r in rows])}\n")
    out.write(f"   any 5-day window:     {stats(weeks)}\n")
    out.write(f"   day before decision:  {stats([r['prev'] for r in rows])}\n")
    out.write(f"   any day:              {stats(days)}\n")

    out.write("\n3. by decision type\n")
    for t in ["hike", "hold", "cut"]:
        part = [r for r in rows if r["type"] == t]
        out.write(f"   {t:4}  week before: {stats([r['week'] for r in part])}\n")
        out.write(f"         day before:  {stats([r['prev'] for r in part])}\n")
    out.close()


def step_bonds():
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


def step_drift():
    def t(v):
        m = sum(v) / len(v)
        sd = (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5
        return m / (sd / len(v) ** 0.5)

    bonds = {}
    for l in open("results/pre_decision/raw/bonds.txt"):
        if l[:2] == "20" and "no data" not in l:
            p = l.replace("|", " ").split()
            bonds[p[0]] = float(p[7])

    r2 = {}
    for b in open("results/key_rate/raw/results_2.txt").read().strip().split("\n\n"):
        lines = b.split("\n")
        r2[lines[0].split()[0]] = {}
        for l in lines[1:]:
            if "%" in l:
                r2[lines[0].split()[0]][l.split(" : ")[0]] = float(l.split(" : ")[-1].rstrip("%"))

    out = open("results/pre_decision/raw/drift.txt", "w")
    out.write("trade IMOEX from 10:34 UTC in the direction of the RGBI +5 surprise\n\n")
    out.write("date        RGBI +5  IMOEX +5 | drift to 11:29  drift to close\n")
    rows = []
    for d in sorted(bonds):
        if d < "2023-07" or "+5" not in r2.get(d, {}):
            continue
        x5 = r2[d]["+5"]
        d60 = ((1 + r2[d]["+60"] / 100) / (1 + x5 / 100) - 1) * 100
        dc = ((1 + r2[d]["to close"] / 100) / (1 + x5 / 100) - 1) * 100
        rows.append([d, bonds[d], x5, d60, dc])
        out.write(f"{d}  {bonds[d]:+6.2f}  {x5:+7.2f}  | {d60:+8.2f}       {dc:+8.2f}\n")
    out.write("\n")

    groups = [["all", rows],
              ["|RGBI +5| >= 0.05", [r for r in rows if abs(r[1]) >= 0.05]],
              ["softer, RGBI +5 >= 0.05", [r for r in rows if r[1] >= 0.05]],
              ["harder, RGBI +5 <= -0.05", [r for r in rows if r[1] <= -0.05]]]
    for name, part in groups:
        for k, lab in [[3, "to 11:29"], [4, "to close"]]:
            pnl = []
            for r in part:
                if r[1] > 0:
                    pnl.append(r[k])
                else:
                    pnl.append(-r[k])
            out.write(f"{name:26} {lab}: n {len(pnl):2}   mean {sum(pnl) / len(pnl):+.3f}%   wins {sum(1 for p in pnl if p > 0)}/{len(pnl)}   t {t(pnl):+.1f}\n")
    out.close()


def step_banks():
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


def step_small_banks():
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


def step_press():
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


for s in steps:
    globals()[f"step_{s}"]()
