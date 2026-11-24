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

# all steps: "daily", "extra", "week", "bonds", "drift", "banks", "small_banks", "press", "minutes", "highlow", "currency", "after", "faster", "bonds_check", "highlow_check", "dev_leak", "morning_check", "sectors"
steps = ["minutes"]

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


def step_minutes():
    # saves raw minute candles for every decision day and for the same weekday one week earlier (control)
    # into data/minutes/DATE_TICKER.csv; files that already exist are skipped
    instruments = pandas.read_csv("data/instruments.csv", dtype=str)
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    os.makedirs("data/minutes", exist_ok=True)

    days = []
    for day in changes["date"]:
        d = datetime.strptime(day, "%Y-%m-%d")
        days.append(f"{d:%Y-%m-%d}")
        days.append(f"{d - timedelta(days=7):%Y-%m-%d}")

    with Client(token) as client:
        # new instruments without a uid in the file: find it by ticker and save it back
        instruments = instruments.fillna("")
        for k in range(len(instruments)):
            if instruments["uid"][k] == "":
                for u in client.instruments.find_instrument(query=instruments["ticker"][k]).instruments:
                    if u.ticker == instruments["ticker"][k]:
                        instruments.loc[k, "uid"] = u.uid
                        break
        instruments.to_csv("data/instruments.csv", index=False)

        for day in days:
            d = datetime.strptime(day, "%Y-%m-%d")
            for k in range(len(instruments)):
                if instruments["uid"][k] == "":
                    continue
                path = f"data/minutes/{day}_{instruments['ticker'][k]}.csv"
                if os.path.exists(path):
                    continue
                start = d.replace(hour=3, minute=0, tzinfo=timezone.utc)
                end = d.replace(hour=21, minute=0, tzinfo=timezone.utc)
                time.sleep(0.1)
                rows = []
                for c in client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=instruments["uid"][k], candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
                    rows.append({"time": f"{c.time:%H:%M}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close), "volume": c.volume})
                pandas.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"]).to_csv(path, index=False)


def step_highlow():
    # around 10:30 UTC on decision days and on control days, from data/minutes:
    #   pre    = price move 10:24 -> 10:29 (the 5 minutes before the release)
    #   vol    = volume 10:25-10:29 divided by normal volume (mean per minute 10:00-10:19, times 5)
    #   high, low, close = the 10:30 minute vs the 10:29 close
    instruments = pandas.read_csv("data/instruments.csv", dtype=str)
    changes = pandas.read_csv("data/cb_kir_decisions.csv")

    def numbers(day, ticker):
        path = f"data/minutes/{day}_{ticker}.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        close = dict(zip(d["time"], d["close"]))
        high = dict(zip(d["time"], d["high"]))
        low = dict(zip(d["time"], d["low"]))
        vol = dict(zip(d["time"], d["volume"]))
        if "10:29" not in close or "10:24" not in close or "10:30" not in close:
            return None
        base = close["10:29"]
        normal = sum(vol.get(f"10:{m:02}", 0) for m in range(0, 20)) / 20 * 5
        pre_vol = sum(vol.get(f"10:{m:02}", 0) for m in range(25, 30))
        return {"pre": pct(close["10:24"], base), "vol": pre_vol / normal if normal > 0 else None,
                "high": pct(base, high["10:30"]), "low": pct(base, low["10:30"]), "close": pct(base, close["10:30"])}

    out = open("results/key_rate/raw/highlow.txt", "w")
    out.write("UTC. pre = move 10:24->10:29, vol = volume 10:25-10:29 / normal (10:00-10:19), high / low / close = minute 10:30 vs 10:29 close\n")
    out.write("control = the same weekday one week earlier\n\n")

    summary = {}
    for day in changes["date"]:
        control = f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}"
        out.write(f"{day}   {changes['rate_before'][changes['date'] == day].iloc[0]:5.2f} -> {changes['rate_after'][changes['date'] == day].iloc[0]:5.2f}\n")
        out.write("ticker  |   pre      vol  |   high     low    close  | control pre   vol\n")
        for t in instruments["ticker"]:
            a = numbers(day, t)
            if a is None:
                continue
            b = numbers(control, t)
            v = f"{a['vol']:6.1f}" if a["vol"] is not None else "     -"
            cb = f"{b['pre']:+6.2f} {b['vol']:6.1f}" if b is not None and b["vol"] is not None else "     -      -"
            out.write(f"{t:7} | {a['pre']:+6.2f}  {v}  | {a['high']:+6.2f}  {a['low']:+6.2f}  {a['close']:+6.2f}  |   {cb}\n")
            if t not in summary:
                summary[t] = {"pre": [], "pre_c": [], "vol": [], "vol_c": [], "far": [], "close": [], "same": 0, "n": 0}
            s = summary[t]
            s["pre"].append(abs(a["pre"]))
            s["far"].append(max(abs(a["high"]), abs(a["low"])))
            s["close"].append(abs(a["close"]))
            if a["vol"] is not None:
                s["vol"].append(a["vol"])
            if b is not None:
                s["pre_c"].append(abs(b["pre"]))
                if b["vol"] is not None:
                    s["vol_c"].append(b["vol"])
            if abs(a["pre"]) >= 0.1:
                s["n"] += 1
                if (a["pre"] > 0) == (a["close"] > 0):
                    s["same"] += 1
        out.write("\n")

    def mean(x):
        return sum(x) / len(x) if len(x) > 0 else 0

    def median(x):
        return sorted(x)[len(x) // 2] if len(x) > 0 else 0

    out.write("summary over all decisions\n")
    out.write("mean |pre| = average size of the move 10:24->10:29; vol = median volume ratio 10:25-10:29\n")
    out.write("far = average farthest point of the 10:30 minute (high or low), close = average |close| of the 10:30 minute\n")
    out.write("same = among days with |pre| >= 0.1%, how often the 10:30 minute went the same way\n\n")
    out.write("ticker  days | mean |pre|  decision  control | vol  decision  control |   far   close | same\n")
    for t in summary:
        s = summary[t]
        out.write(f"{t:7} {len(s['pre']):4} |            {mean(s['pre']):6.3f}%  {mean(s['pre_c']):6.3f}% |      {median(s['vol']):6.1f}  {median(s['vol_c']):6.1f}  | {mean(s['far']):5.2f}%  {mean(s['close']):5.2f}% | {s['same']}/{s['n']}\n")
    out.close()


def step_currency():
    # currency and gold around the decision, from data/minutes (no API needed)
    # surprise = RGBI 10:29 -> 11:29 (bonds up = softer than expected)
    # for each instrument: move 10:29 -> 10:30, -> 10:34, -> 11:29, and 10:24 -> 10:29 before the release
    tickers = ["IMOEX", "USDRUBF", "CNYRUBF", "CNYRUB_TOM", "GLDRUB_TOM", "GLDRUBF"]
    changes = pandas.read_csv("data/cb_kir_decisions.csv")

    def close(day, ticker):
        path = f"data/minutes/{day}_{ticker}.csv"
        if not os.path.exists(path):
            return {}
        d = pandas.read_csv(path)
        return dict(zip(d["time"], d["close"]))

    def move(c, a, b):
        if a in c and b in c:
            return pct(c[a], c[b])
        return None

    rows = []
    for day in changes["date"]:
        control = f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}"
        r = {"date": day, "surprise": move(close(day, "RGBI"), "10:29", "11:29")}
        for t in tickers:
            c = close(day, t)
            r[t + " +1"] = move(c, "10:29", "10:30")
            r[t + " +5"] = move(c, "10:29", "10:34")
            r[t + " +60"] = move(c, "10:29", "11:29")
            r[t + " pre"] = move(c, "10:24", "10:29")
            r[t + " pre_control"] = move(close(control, t), "10:24", "10:29")
        rows.append(r)

    def f(x):
        return f"{x:+6.2f}" if x is not None else "     -"

    out = open("results/key_rate/raw/currency.txt", "w")
    out.write("UTC. surprise = RGBI 10:29 -> 11:29 (bonds up = softer than expected). USD/RUB up = ruble weaker\n\n")
    out.write("date        surprise |" + "".join(f" {t:>11} +1    +60 |" for t in tickers) + "\n")
    for r in rows:
        out.write(f"{r['date']}  {f(r['surprise'])} |" + "".join(f"      {f(r[t + ' +1'])} {f(r[t + ' +60'])} |" for t in tickers) + "\n")

    out.write("\ncorr with the surprise, and average size of the move (mean |x|)\n")
    for name, part in [["before jul 2023", [r for r in rows if r["date"] < "2023-07-01"]], ["from jul 2023", [r for r in rows if r["date"] >= "2023-07-01"]]]:
        out.write(f"\n{name}\n")
        out.write("ticker        days |  corr +1   +5  +60 | mean |x| +1    +60 | before release |pre|: decision  control\n")
        for t in tickers:
            ok = [r for r in part if r["surprise"] is not None and r[t + " +60"] is not None and r[t + " +1"] is not None and r[t + " +5"] is not None]
            if len(ok) < 5:
                out.write(f"{t:12} {len(ok):4}  | too few days\n")
                continue
            s = [r["surprise"] for r in ok]
            c1 = corr(s, [r[t + " +1"] for r in ok])
            c5 = corr(s, [r[t + " +5"] for r in ok])
            c60 = corr(s, [r[t + " +60"] for r in ok])
            a1 = sum(abs(r[t + " +1"]) for r in ok) / len(ok)
            a60 = sum(abs(r[t + " +60"]) for r in ok) / len(ok)
            pre = sorted(abs(r[t + " pre"]) for r in part if r[t + " pre"] is not None)
            pc = sorted(abs(r[t + " pre_control"]) for r in part if r[t + " pre_control"] is not None and r["date"] != "2021-04-23")
            mp = f"{pre[len(pre) // 2]:.3f}%" if len(pre) > 0 else "-"
            mc = f"{pc[len(pc) // 2]:.3f}%" if len(pc) > 0 else "-"
            out.write(f"{t:12} {len(ok):4}  | {c1:+.2f} {c5:+.2f} {c60:+.2f} |      {a1:.2f}%  {a60:.2f}% |   median {mp}  {mc}\n")
    out.write("\ncorr noise level: about 2 / sqrt(days)\n")
    out.close()


def step_after():
    # 1. morning of the decision day: IMOEX 07:00 -> 10:29 UTC, vs the control day (one week earlier)
    # 2. days after: does the market keep going in the direction of the decision day?
    #    rule = sign(day move) * move over the next 1 / 3 / 5 days; positive = the move continued
    # 3. check against luck: the same rule on ordinary Fridays, many random draws
    import random
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    daily = pandas.read_csv("data/imoex_daily.csv")
    dates = list(daily["date"])
    close = list(daily["close"])
    where = {d: i for i, d in enumerate(dates)}

    def minute_close(day, hm):
        path = f"data/minutes/{day}_IMOEX.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        c = dict(zip(d["time"], d["close"]))
        return c.get(hm)

    def morning(day):
        a = minute_close(day, "07:00")
        b = minute_close(day, "10:29")
        if a is None or b is None:
            return None
        return pct(a, b)

    def rule(day, k):
        i = where.get(day)
        if i is None or i < 1 or i + k >= len(close):
            return None
        sign = 1 if close[i] > close[i - 1] else -1
        return sign * pct(close[i], close[i + k])

    def stats(v):
        v = [x for x in v if x is not None]
        n = len(v)
        if n < 3:
            return f"n {n}"
        m = sum(v) / n
        sd = (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5
        up = sum(1 for x in v if x > 0)
        return f"n {n:3}  mean {m:+.2f}%  t {m / (sd / n ** 0.5):+.1f}  positive {up}/{n}"

    def kind(k):
        if changes["rate_after"][k] > changes["rate_before"][k]:
            return "hike"
        if changes["rate_after"][k] < changes["rate_before"][k]:
            return "cut"
        return "hold"

    out = open("results/key_rate/raw/after.txt", "w")
    out.write("IMOEX. control = the same weekday one week earlier\n\n")
    out.write("1. morning 07:00 -> 10:29 UTC\n")
    for name, test in [["before jul 2023", lambda d: d < "2023-07-01"], ["from jul 2023", lambda d: d >= "2023-07-01"]]:
        out.write(f"\n{name}\n")
        for kname in ["all", "hike", "hold", "cut"]:
            dec = []
            ctl = []
            for k in range(len(changes)):
                day = changes["date"][k]
                if not test(day) or (kname != "all" and kind(k) != kname):
                    continue
                control = f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}"
                dec.append(morning(day))
                ctl.append(morning(control))
            out.write(f"   {kname:5} decision {stats(dec)}\n         control  {stats(ctl)}\n")

    out.write("\n2. days after the decision: sign of the decision day * move over the next k days\n")
    decision_days = set(changes["date"])
    for name, test in [["before jul 2023", lambda d: d < "2023-07-01"], ["from jul 2023", lambda d: d >= "2023-07-01"]]:
        out.write(f"\n{name}\n")
        for k in [1, 3, 5]:
            dec = [rule(d, k) for d in changes["date"] if test(d)]
            no_dec = [rule(d, k) for d in changes["date"] if test(d) and d != "2024-12-20"]
            fridays = [rule(d, k) for d in dates if test(d) and d not in decision_days and datetime.strptime(d, "%Y-%m-%d").weekday() == 4]
            out.write(f"   +{k} days  decision {stats(dec)}\n")
            out.write(f"            without 20.12.2024 {stats(no_dec)}\n")
            out.write(f"            all other Fridays {stats(fridays)}\n")

            # 3. luck: draw as many random Fridays as there are decisions, 10000 times
            dec = [x for x in dec if x is not None]
            fridays = [x for x in fridays if x is not None]
            if len(dec) > 0 and len(fridays) >= len(dec):
                real = sum(dec) / len(dec)
                better = 0
                for _ in range(10000):
                    pick = random.sample(fridays, len(dec))
                    if sum(pick) / len(pick) >= real:
                        better += 1
                out.write(f"            random Fridays as good or better: {better / 100:.1f}% of 10000 draws\n")
    out.close()


def step_faster():
    # is the reaction to the decision bigger and faster than before jul 2023?
    # base = IMOEX close at 10:29 UTC, moves to 10:30 (1 min), 10:39 (10 min), 11:29 (1 hour), 15:39 (close)
    # 1. mean |move| on decision days vs control days (same weekday a week earlier), ratio, bootstrap by dates
    # 2. by year: how much of the 1 hour move is already there after 1 minute, and same sign or not
    import random
    random.seed(1)
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    windows = [["1 min", "10:30"], ["10 min", "10:39"], ["1 hour", "11:29"], ["close", "15:39"]]

    def moves(day):
        path = f"data/minutes/{day}_IMOEX.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        c = dict(zip(d["time"], d["close"]))
        if "10:29" not in c:
            return None
        base = c["10:29"]
        # one bad print at 10:29 (16.04.2021: -2.6% and back in the next minute) -> use 10:28
        if "10:28" in c and "10:30" in c and abs(pct(c["10:28"], base)) > 1 and abs(pct(c["10:28"], c["10:30"])) < 0.2:
            base = c["10:28"]
        res = []
        for name, hm in windows:
            # last minute at or before hm (the index sometimes skips a minute)
            t = [x for x in d["time"] if x <= hm]
            res.append(pct(base, c[t[-1]]))
        return res

    def mean(v):
        return sum(v) / len(v)

    out = open("results/key_rate/raw/faster.txt", "w")
    out.write("IMOEX, UTC, base = close at 10:29. control = the same weekday one week earlier\n")
    out.write("mean |move| on decision days and control days, ratio = decision / control, 95% interval = bootstrap by dates\n")
    for name, test in [["before jul 2023", lambda d: d < "2023-07-01"], ["from jul 2023", lambda d: d >= "2023-07-01"]]:
        dec = []
        ctl = []
        for day in changes["date"]:
            if not test(day):
                continue
            control = f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}"
            a = moves(day)
            b = moves(control)
            if a is None or b is None:
                continue
            dec.append(a)
            ctl.append(b)
        n = len(dec)
        out.write(f"\n{name}, {n} days\n")
        out.write("window    decision  control   ratio   95%\n")
        for w in range(len(windows)):
            x = [abs(v[w]) for v in dec]
            y = [abs(v[w]) for v in ctl]
            r = mean(x) / mean(y)
            boot = []
            for _ in range(10000):
                pick = [random.randrange(n) for _ in range(n)]
                boot.append(mean([x[i] for i in pick]) / mean([y[i] for i in pick]))
            boot.sort()
            out.write(f"{windows[w][0]:8}  {mean(x):6.3f}%  {mean(y):6.3f}%  {r:6.1f}   [{boot[250]:.1f}; {boot[9750]:.1f}]\n")

    out.write("\nby year: share = (1 min move) / (1 hour move), median over decisions; same sign = 1 min and 1 hour in the same direction\n")
    out.write("year  days  median share  same sign\n")
    for year in range(2021, 2027):
        v = []
        for day in changes["date"]:
            if day[:4] != str(year):
                continue
            a = moves(day)
            if a is None or a[2] == 0:
                continue
            v.append(a[0] / a[2])
        if len(v) == 0:
            continue
        v.sort()
        med = v[len(v) // 2] if len(v) % 2 == 1 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
        same = sum(1 for x in v if x > 0)
        out.write(f"{year}  {len(v):4}  {med:12.2f}  {same:4}/{len(v)}\n")
    for name, test in [["before jul 2023", lambda d: d < "2023-07-01"], ["from jul 2023", lambda d: d >= "2023-07-01"]]:
        same = 0
        n = 0
        for day in changes["date"]:
            a = moves(day)
            if not test(day) or a is None or a[2] == 0:
                continue
            n += 1
            if a[0] * a[2] > 0:
                same += 1
        out.write(f"{name}: same sign {same}/{n}\n")
    out.close()


def step_bonds_check():
    # how solid is "bonds explain stocks"? since jul 2023, from data/minutes, base = close at 10:29 UTC
    # 1. corr of the first hour IMOEX vs RGBI: bootstrap by dates, without each date, rank corr
    # 2. who is first: IMOEX first minute vs RGBI after it (10:30 -> 11:29), and the other way round
    # 3. key vs regular meetings: is the difference in corr more than a random split gives
    import random
    random.seed(1)
    changes = pandas.read_csv("data/cb_kir_decisions.csv")

    def closes(day, ticker):
        path = f"data/minutes/{day}_{ticker}.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        return dict(zip(d["time"], d["close"]))

    def at(c, hm):
        # last price at or before hm
        t = [x for x in c if x <= hm]
        return c[max(t)] if t else None

    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for k, i in enumerate(order):
            r[i] = k + 1
        return r

    days = []
    stocks = []
    bonds = []
    s1 = []
    b_after = []
    s_after = []
    b5 = []
    for day in changes["date"]:
        if day < "2023-07-01":
            continue
        i = closes(day, "IMOEX")
        b = closes(day, "RGBI")
        if i is None or b is None or "10:29" not in i or "10:29" not in b:
            continue
        days.append(day)
        stocks.append(pct(i["10:29"], at(i, "11:29")))
        bonds.append(pct(b["10:29"], at(b, "11:29")))
        s1.append(pct(i["10:29"], at(i, "10:30")))
        b_after.append(pct(at(b, "10:30"), at(b, "11:29")))
        b5.append(pct(b["10:29"], at(b, "10:34")))
        s_after.append(pct(at(i, "10:34"), at(i, "11:29")))
    n = len(days)

    out = open("results/pre_decision/raw/bonds_check.txt", "w")
    out.write(f"since jul 2023, {n} decisions, UTC, base = close at 10:29. noise level for corr about {2 / n ** 0.5:.2f}\n\n")
    out.write("1. first hour, IMOEX vs RGBI\n")
    out.write(f"   corr {corr(stocks, bonds):+.2f}, rank corr {corr(ranks(stocks), ranks(bonds)):+.2f}\n")
    boot = []
    for _ in range(10000):
        pick = [random.randrange(n) for _ in range(n)]
        boot.append(corr([stocks[k] for k in pick], [bonds[k] for k in pick]))
    boot.sort()
    out.write(f"   bootstrap by dates 95%: [{boot[250]:+.2f}; {boot[9750]:+.2f}]\n")
    loo = []
    for k in range(n):
        loo.append([corr(stocks[:k] + stocks[k + 1:], bonds[:k] + bonds[k + 1:]), days[k]])
    loo.sort()
    out.write(f"   without one date: from {loo[0][0]:+.2f} (without {loo[0][1]}) to {loo[-1][0]:+.2f}\n")

    out.write("\n2. who is first\n")
    out.write(f"   IMOEX first minute vs RGBI after it (10:30 -> 11:29): corr {corr(s1, b_after):+.2f}\n")
    out.write(f"   RGBI first 5 minutes vs IMOEX after them (10:34 -> 11:29): corr {corr(b5, s_after):+.2f}\n")
    out.write("   if stocks predict later bonds, RGBI is slow and partly follows stocks: it's not a clean outside measure of the surprise\n")

    out.write("\n3. key meetings (feb, apr, jul, oct + 15 sep 2023) vs regular\n")
    key = [d[5:7] in ["02", "04", "07", "10"] or d == "2023-09-15" for d in days]
    ks = [stocks[k] for k in range(n) if key[k]]
    kb = [bonds[k] for k in range(n) if key[k]]
    rs = [stocks[k] for k in range(n) if not key[k]]
    rb = [bonds[k] for k in range(n) if not key[k]]
    diff = corr(rs, rb) - corr(ks, kb)
    out.write(f"   key {len(ks)}: corr {corr(ks, kb):+.2f}   regular {len(rs)}: corr {corr(rs, rb):+.2f}   difference {diff:+.2f}\n")
    better = 0
    for _ in range(10000):
        lab = key[:]
        random.shuffle(lab)
        a = [k for k in range(n) if lab[k]]
        b = [k for k in range(n) if not lab[k]]
        d = corr([stocks[k] for k in b], [bonds[k] for k in b]) - corr([stocks[k] for k in a], [bonds[k] for k in a])
        if abs(d) >= abs(diff):
            better += 1
    out.write(f"   random splits with the same or bigger difference: {better / 100:.1f}% of 10000\n")
    out.close()


def step_highlow_check():
    # what close hides: high and low inside the minutes around 10:30 UTC
    # base = close at 10:29, control = same weekday a week earlier
    # range   = (high - low) of the minute 10:30
    # retrace = which part of a big move inside a minute came back by its close
    #           decision days: the minute 10:30; ordinary: every minute of the control days that went >= 0.3%
    # hidden  = a minute where the price went >= 0.3% from the previous close, but closed within 1/3 of that
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    tickers = ["IMOEX", "IMOEXF", "SBER", "VTBR", "T", "GAZP", "LKOH", "SMLT"]

    def candles(day, ticker):
        path = f"data/minutes/{day}_{ticker}.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        res = {}
        for k in range(len(d)):
            res[d["time"][k]] = [d["open"][k], d["high"][k], d["low"][k], d["close"][k], d["volume"][k]]
        return res

    def move(prev, candle):
        # how far the minute went from the previous close, where it closed, and the part that came back
        o, h, l, cl, v = candle
        up = (h - prev) / prev * 100
        down = (l - prev) / prev * 100
        went = up if abs(up) >= abs(down) else down
        closed = (cl - prev) / prev * 100
        return went, closed, (went - closed) / went if went != 0 else 0

    def mean(v):
        return sum(v) / len(v)

    def control_of(day):
        return f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}"

    new = [d for d in changes["date"] if d >= "2023-07-01"]
    out = open("results/key_rate/raw/highlow_check.txt", "w")
    out.write("UTC, since jul 2023. base = close at 10:29, control = same weekday a week earlier\n")

    out.write("\n1. range of the minute 10:30 (high - low)\n")
    out.write("ticker  days   decision   control   ratio\n")
    for t in tickers:
        rd = []
        rc = []
        for day in new:
            a = candles(day, t)
            b = candles(control_of(day), t)
            if a is None or b is None or "10:29" not in a or "10:30" not in a or "10:29" not in b or "10:30" not in b:
                continue
            rd.append((a["10:30"][1] - a["10:30"][2]) / a["10:29"][3] * 100)
            rc.append((b["10:30"][1] - b["10:30"][2]) / b["10:29"][3] * 100)
        if len(rd) >= 5:
            out.write(f"{t:6} {len(rd):4}   {mean(rd):6.3f}%   {mean(rc):6.3f}%  {mean(rd) / mean(rc):5.1f}\n")

    out.write("\n2. retrace: part of the move that came back by the close of the minute\n")
    out.write("ticker   minute 10:30 on decision days   big minutes (>= 0.3%) on ordinary days\n")
    for t in tickers:
        dec = []
        ordi = []
        for day in new:
            a = candles(day, t)
            if a is not None and "10:29" in a and "10:30" in a:
                went, closed, back = move(a["10:29"][3], a["10:30"])
                if abs(went) >= 0.3:
                    dec.append(back)
            b = candles(control_of(day), t)
            if b is None:
                continue
            times = sorted(b)
            for k in range(1, len(times)):
                if "07:00" <= times[k] <= "15:39":
                    went, closed, back = move(b[times[k - 1]][3], b[times[k]])
                    if abs(went) >= 0.3:
                        ordi.append(back)
        if len(dec) >= 5 and len(ordi) >= 5:
            out.write(f"{t:6}   {mean(dec) * 100:4.0f}% ({len(dec)} days)                 {mean(ordi) * 100:4.0f}% ({len(ordi)} minutes)\n")

    out.write("\n3. hidden moves (went >= 0.3%, closed within 1/3 of it): how many instrument-minutes\n")
    out.write("window          decision days   control days\n")
    for w, lo, hi in [["10:25-10:29", "10:25", "10:29"], ["10:30-10:35", "10:30", "10:35"]]:
        cnt = [0, 0]
        for j, which in enumerate(["decision", "control"]):
            for day in new:
                d = day if which == "decision" else control_of(day)
                for t in tickers:
                    c = candles(d, t)
                    if c is None:
                        continue
                    times = sorted(c)
                    for k in range(1, len(times)):
                        if lo <= times[k] <= hi:
                            went, closed, back = move(c[times[k - 1]][3], c[times[k]])
                            if abs(went) >= 0.3 and abs(closed) < abs(went) / 3:
                                cnt[j] += 1
        out.write(f"{w}     {cnt[0]:6}          {cnt[1]:6}\n")

    out.write("\n4. hidden moves before the release (10:25-10:29) on decision days, all years\n")
    out.write("date        ticker  time   went     closed   first minute after (10:29 -> 10:30)\n")
    for day in changes["date"]:
        for t in tickers:
            c = candles(day, t)
            if c is None or "10:29" not in c or "10:30" not in c:
                continue
            times = sorted(c)
            for k in range(1, len(times)):
                if "10:25" <= times[k] <= "10:29":
                    went, closed, back = move(c[times[k - 1]][3], c[times[k]])
                    if abs(went) >= 0.3 and abs(closed) < abs(went) / 3:
                        after = pct(c["10:29"][3], c["10:30"][3])
                        out.write(f"{day}  {t:6}  {times[k]}  {went:+6.2f}%  {closed:+6.2f}%   {after:+6.2f}%\n")
    out.close()


def step_dev_leak():
    # if someone knows the decision, the best place to trade it is developers: they move about 2x the index
    # check: do developers move relative to the index BEFORE 10:30 in the direction the market goes AFTER?
    # developers = average of SMLT, LSRG, ETLN, GLRX (whatever has a price), relative = developers - IMOEX
    # after = IMOEX 10:29 -> 11:29. control = same weekday a week earlier, same windows
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    devs = ["SMLT", "LSRG", "ETLN", "GLRX"]
    windows = [["morning 07:00-10:29", "07:00"], ["10:00-10:29", "10:00"], ["10:24-10:29", "10:24"]]

    def closes(day, ticker):
        path = f"data/minutes/{day}_{ticker}.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        return dict(zip(d["time"], d["close"]))

    def at(c, hm):
        t = [x for x in c if x <= hm]
        return c[max(t)] if t else None

    def numbers(day):
        i = closes(day, "IMOEX")
        if i is None or "10:29" not in i:
            return None
        # one bad print at 10:29 (16.04.2021) breaks everything, skip such a day
        if "10:28" in i and "10:30" in i and abs(pct(i["10:28"], i["10:29"])) > 1 and abs(pct(i["10:28"], i["10:30"])) < 0.2:
            return None
        res = {"after": pct(i["10:29"], at(i, "11:29")), "dev_after": None}
        for name, start in windows:
            if at(i, start) is None:
                return None
            moves = []
            moves_after = []
            for t in devs:
                c = closes(day, t)
                if c is None or at(c, start) is None or at(c, "10:29") is None:
                    continue
                moves.append(pct(at(c, start), at(c, "10:29")))
                if at(c, "11:29") is not None:
                    moves_after.append(pct(at(c, "10:29"), at(c, "11:29")))
            if len(moves) == 0:
                return None
            res[name] = sum(moves) / len(moves) - pct(at(i, start), i["10:29"])
            if len(moves_after) > 0:
                res["dev_after"] = sum(moves_after) / len(moves_after) - res["after"]
        return res

    out = open("results/pre_decision/raw/dev_leak.txt", "w")
    out.write("developers (SMLT, LSRG, ETLN, GLRX) minus IMOEX before 10:30 UTC vs IMOEX after (10:29 -> 11:29)\n")
    out.write("control = same weekday a week earlier. same sign = developers before went the way IMOEX went after\n")
    for pname, test in [["before jul 2023", lambda d: d < "2023-07-01"], ["from jul 2023", lambda d: d >= "2023-07-01"]]:
        dec = []
        ctl = []
        for day in changes["date"]:
            if not test(day):
                continue
            a = numbers(day)
            b = numbers(f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}")
            if a is not None:
                dec.append(a)
            if b is not None:
                ctl.append(b)
        out.write(f"\n{pname}: {len(dec)} decision days, {len(ctl)} control days, noise level for corr about {2 / len(dec) ** 0.5:.2f}\n")
        out.write("window                 | decision: corr  same sign  mean |rel| | control: corr  same sign  mean |rel|\n")
        for name, start in windows:
            line = f"{name:22} |"
            for v in [dec, ctl]:
                x = [r[name] for r in v]
                y = [r["after"] for r in v]
                same = sum(1 for k in range(len(x)) if x[k] * y[k] > 0)
                line += f"   {corr(x, y):+.2f}    {same:2}/{len(x):2}      {sum(abs(z) for z in x) / len(x):.2f}%   |"
            out.write(line + "\n")
        part = [r for r in dec if r["dev_after"] is not None]
        x = [r["after"] for r in part]
        y = [r["dev_after"] for r in part]
        out.write(f"   check: developers minus IMOEX after the release vs IMOEX after: corr {corr(x, y):+.2f}, slope {slope(x, y):+.2f} (positive = developers move more than the index)\n")
    out.close()


def step_morning_check():
    # does the market go up in the morning before a decision? (in the US: "pre-FOMC drift", stocks rise before Fed decisions)
    # IMOEX, UTC. windows: previous day close -> 10:29, 07:00 -> 10:29, and the morning split into 07:00 -> 08:30 and 08:30 -> 10:29
    # control = same weekday a week earlier. difference = decision - control for the same pair, bootstrap by dates
    # plus: does the morning guess where the market goes after the release (10:29 -> 11:29)?
    import random
    random.seed(1)
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    daily = pandas.read_csv("data/imoex_daily.csv")
    prev_close = {}
    for k in range(1, len(daily)):
        prev_close[daily["date"][k]] = daily["close"][k - 1]
    windows = [["prev close -> 10:29", None, "10:29"], ["07:00 -> 10:29", "07:00", "10:29"], ["07:00 -> 08:30", "07:00", "08:30"], ["08:30 -> 10:29", "08:30", "10:29"]]

    def closes(day):
        path = f"data/minutes/{day}_IMOEX.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        return dict(zip(d["time"], d["close"]))

    def at(c, hm):
        t = [x for x in c if x <= hm]
        return c[max(t)] if t else None

    def moves(day):
        c = closes(day)
        if c is None or "10:29" not in c or at(c, "07:00") is None:
            return None
        # one bad print at 10:29 (16.04.2021): use 10:28
        if "10:28" in c and "10:30" in c and abs(pct(c["10:28"], c["10:29"])) > 1 and abs(pct(c["10:28"], c["10:30"])) < 0.2:
            c["10:29"] = c["10:28"]
        res = []
        for name, a, b in windows:
            if a is None:
                res.append(pct(prev_close[day], c[b]) if day in prev_close else None)
            else:
                res.append(pct(at(c, a), at(c, b)))
        res.append(pct(c["10:29"], at(c, "11:29")))
        return res

    def mean(v):
        return sum(v) / len(v)

    out = open("results/pre_decision/raw/morning_check.txt", "w")
    out.write("IMOEX, UTC. control = same weekday a week earlier, difference = decision - control for the same pair, 95% = bootstrap by dates\n")
    for pname, test in [["before jul 2023", lambda d: d < "2023-07-01"], ["from jul 2023", lambda d: d >= "2023-07-01"]]:
        pairs = []
        for day in changes["date"]:
            if not test(day):
                continue
            a = moves(day)
            b = moves(f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}")
            if a is not None and b is not None:
                pairs.append([day, a, b])
        n = len(pairs)
        out.write(f"\n{pname}, {n} pairs\n")
        out.write("window               decision   up    control   up    difference  95%\n")
        for w in range(len(windows)):
            p2 = [x for x in pairs if x[1][w] is not None and x[2][w] is not None]
            d = [x[1][w] for x in p2]
            c = [x[2][w] for x in p2]
            diff = [d[k] - c[k] for k in range(len(d))]
            boot = []
            for _ in range(10000):
                pick = [random.choice(diff) for _ in diff]
                boot.append(mean(pick))
            boot.sort()
            up_d = sum(1 for x in d if x > 0)
            up_c = sum(1 for x in c if x > 0)
            out.write(f"{windows[w][0]:20} {mean(d):+6.2f}%  {up_d:2}/{len(d):2}  {mean(c):+6.2f}%  {up_c:2}/{len(c):2}   {mean(diff):+6.2f}%  [{boot[250]:+.2f}; {boot[9750]:+.2f}]\n")
        x = [p2[1][1] for p2 in pairs]
        y = [p2[1][4] for p2 in pairs]
        out.write(f"does the morning 07:00 -> 10:29 guess the move after the release (10:29 -> 11:29)? corr {corr(x, y):+.2f}, same sign {sum(1 for k in range(n) if x[k] * y[k] > 0)}/{n} (noise level about {2 / n ** 0.5:.2f})\n")
        out.write("by year, 07:00 -> 10:29 on decision days: ")
        for year in range(2021, 2027):
            v = [p2[1][1] for p2 in pairs if p2[0][:4] == str(year)]
            if len(v) > 0:
                out.write(f"{year}: {mean(v):+.2f}% ({sum(1 for z in v if z > 0)}/{len(v)})  ")
        out.write("\n")
    out.close()


def step_sectors():
    # who reacts to the rate the most? first hour after the release (10:29 -> 11:29 UTC), since jul 2023
    # beta = slope of the group move on the IMOEX move: 2 = the group moves 2x the index
    # decision days vs control days (same weekday a week earlier), difference with bootstrap by dates
    import random
    random.seed(1)
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    groups = [["developers", ["SMLT", "LSRG", "ETLN", "GLRX"]],
              ["big banks", ["SBER", "VTBR", "T"]],
              ["mid banks", ["BSPB", "SVCB", "MBNK", "CBOM"]],
              ["retail", ["X5", "MGNT"]],
              ["Aeroflot", ["AFLT"]],
              ["oil and gas", ["LKOH", "ROSN", "GAZP"]]]

    def closes(day, ticker):
        path = f"data/minutes/{day}_{ticker}.csv"
        if not os.path.exists(path):
            return None
        d = pandas.read_csv(path)
        return dict(zip(d["time"], d["close"]))

    def at(c, hm):
        t = [x for x in c if x <= hm]
        return c[max(t)] if t else None

    def hour(day, ticker):
        c = closes(day, ticker)
        if c is None or "10:29" not in c or at(c, "11:29") is None:
            return None
        return pct(c["10:29"], at(c, "11:29"))

    def group_move(day, tickers):
        v = [hour(day, t) for t in tickers]
        v = [x for x in v if x is not None]
        return sum(v) / len(v) if v else None

    new = [d for d in changes["date"] if d >= "2023-07-01"]
    out = open("results/sectors/raw/sectors.txt", "w")
    out.write("first hour 10:29 -> 11:29 UTC, since jul 2023. beta = slope of the group on IMOEX, control = same weekday a week earlier\n")
    out.write("group = average of its stocks that have a price\n\n")
    out.write("group         days | beta decision  beta control | difference  95%\n")
    for name, tickers in groups:
        rows = []
        for day in new:
            control = f"{datetime.strptime(day, '%Y-%m-%d') - timedelta(days=7):%Y-%m-%d}"
            a = [hour(day, "IMOEX"), group_move(day, tickers)]
            b = [hour(control, "IMOEX"), group_move(control, tickers)]
            if None in a or None in b:
                continue
            rows.append([a, b])
        n = len(rows)
        bd = slope([r[0][0] for r in rows], [r[0][1] for r in rows])
        bc = slope([r[1][0] for r in rows], [r[1][1] for r in rows])
        boot = []
        for _ in range(10000):
            pick = [random.choice(rows) for _ in rows]
            boot.append(slope([r[0][0] for r in pick], [r[0][1] for r in pick]) - slope([r[1][0] for r in pick], [r[1][1] for r in pick]))
        boot.sort()
        out.write(f"{name:12} {n:4}  |     {bd:5.2f}         {bc:5.2f}     |   {bd - bc:+5.2f}   [{boot[250]:+.2f}; {boot[9750]:+.2f}]\n")

    out.write("\nsingle stocks, decision days: beta and corr with IMOEX\n")
    for name, tickers in groups:
        for t in tickers:
            x = []
            y = []
            for day in new:
                a = hour(day, "IMOEX")
                b = hour(day, t)
                if a is not None and b is not None:
                    x.append(a)
                    y.append(b)
            if len(x) >= 10:
                out.write(f"   {name:12} {t:5} days {len(x):2}   beta {slope(x, y):5.2f}   corr {corr(x, y):+.2f}\n")

    # developers minus oil and gas: the most and the least rate-sensitive groups
    out.write("\ndevelopers minus oil and gas, first hour: does it go with the bond surprise (RGBI 10:29 -> 11:29)?\n")
    x = []
    y = []
    z = []
    for day in new:
        dv = group_move(day, ["SMLT", "LSRG", "ETLN", "GLRX"])
        og = group_move(day, ["LKOH", "ROSN", "GAZP"])
        b = hour(day, "RGBI")
        i = hour(day, "IMOEX")
        if None in [dv, og, b, i]:
            continue
        x.append(dv - og)
        y.append(b)
        z.append(i)
    out.write(f"   days {len(x)}: corr with RGBI {corr(x, y):+.2f}, corr with IMOEX {corr(x, z):+.2f}\n")
    out.close()


for s in steps:
    globals()[f"step_{s}"]()
