# One-minute spikes: the price jumps and comes back within a minute or two.
# Known cases from the news + 24.10.2025 from high/low. For every case: minute candles of the whole day
# for the instrument that jumped, its neighbours and RVI (volatility index). Times UTC.
# Steps: "download" needs the token, "cases" and "rvi" only read data/flash/.
from t_tech.invest import Client, CandleInterval
from t_tech.invest.schemas import CandleSource
from datetime import datetime, timedelta, timezone
import os
import time
import pandas
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

# all steps: "download", "cases", "rvi", "history", "detect", "before", "cost"
steps = ["detect"]

# date, time of the spike (UTC, "" = find it), main instrument, the rest to compare
cases = [
    ["2022-07-21", "07:12", "USD000UTSTOM", ["CNYRUB_TOM", "EUR_RUB__TOM", "SiU2", "IMOEX", "RVI"]],
    ["2022-08-19", "07:00", "USD000UTSTOM", ["CNYRUB_TOM", "EUR_RUB__TOM", "SiU2", "IMOEX", "RVI"]],
    ["2023-08-25", "14:28", "USD000UTSTOM", ["CNYRUB_TOM", "SiU3", "IMOEX", "RVI"]],
    ["2024-01-16", "", "USD000UTSTOM", ["CNYRUB_TOM", "SiH4", "IMOEX", "RVI"]],
    ["2024-02-09", "11:15", "USD000UTSTOM", ["CNYRUB_TOM", "SiH4", "IMOEX", "RVI"]],
    ["2025-06-09", "", "SiM5", ["USDRUBF", "CNYRUB_TOM", "IMOEX", "RVI"]],
    ["2025-09-16", "08:33", "MXU5", ["IMOEXF", "IMOEX", "SBER", "RVI"]],
    ["2025-10-24", "10:29", "IMOEXF", ["IMOEX", "SBER", "LKOH", "USDRUBF", "RVI"]],
]


def get_price(x):
    return x.units + x.nano * 1e-9


def pct(a, b):
    return (b - a) / a * 100


def step_download():
    os.makedirs("data/flash", exist_ok=True)
    uids = {}
    with Client(token) as client:
        for day, hm, main, rest in cases:
            for ticker in [main] + rest:
                path = f"data/flash/{day}_{ticker}.csv"
                if os.path.exists(path):
                    continue
                if ticker not in uids:
                    uids[ticker] = ""
                    for u in client.instruments.find_instrument(query=ticker).instruments:
                        if u.ticker == ticker:
                            uids[ticker] = u.uid
                            break
                    time.sleep(0.2)
                if uids[ticker] == "":
                    print(ticker, "not found")
                    continue
                d = datetime.strptime(day, "%Y-%m-%d")
                rows = []
                for c in client.market_data.get_candles(from_=d.replace(hour=3, tzinfo=timezone.utc), to=d.replace(hour=21, tzinfo=timezone.utc), interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uids[ticker], candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
                    rows.append({"time": f"{c.time:%H:%M}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close), "volume": c.volume})
                pandas.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"]).to_csv(path, index=False)
                print(day, ticker, len(rows), "minutes")
                time.sleep(0.2)
        # RVI by day since 2021, for the "rvi" step
        if not os.path.exists("data/flash/rvi_daily.csv") and uids.get("RVI", "") != "":
            rows = []
            for year in range(2021, 2027):
                for c in client.market_data.get_candles(from_=datetime(year, 1, 1, tzinfo=timezone.utc), to=datetime(year, 12, 31, tzinfo=timezone.utc), interval=CandleInterval.CANDLE_INTERVAL_DAY, instrument_id=uids["RVI"], candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
                    rows.append({"date": f"{c.time:%Y-%m-%d}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close)})
                time.sleep(0.2)
            pandas.DataFrame(rows, columns=["date", "open", "high", "low", "close"]).to_csv("data/flash/rvi_daily.csv", index=False)
            print("RVI daily", len(rows), "days")


def load(day, ticker):
    path = f"data/flash/{day}_{ticker}.csv"
    if not os.path.exists(path):
        return None
    d = pandas.read_csv(path)
    if len(d) == 0:
        return None
    return d


def spikes(d):
    # every minute: how far it went from the previous close and where it closed
    res = []
    for k in range(1, len(d)):
        prev = d["close"][k - 1]
        up = pct(prev, d["high"][k])
        down = pct(prev, d["low"][k])
        went = up if abs(up) >= abs(down) else down
        res.append([d["time"][k], went, pct(prev, d["close"][k]), d["volume"][k]])
    return res


def step_cases():
    out = open("results/flash/raw/cases.txt", "w")
    out.write("UTC. went = how far the minute went from the previous close (high or low), closed = where it closed, both in %\n")
    out.write("normal volume = median volume per minute of that day\n")
    for day, hm, main, rest in cases:
        d = load(day, main)
        out.write(f"\n===== {day} {main}\n")
        if d is None:
            out.write("no data\n")
            continue
        s = spikes(d)
        if hm == "":
            hm = max(s, key=lambda x: abs(x[1]))[0]
            out.write(f"biggest minute of the day: {hm}\n")
        out.write("ticker          " + "".join(f"{t:>16}" for t in [main] + rest) + "\n")
        data = {}
        for t in [main] + rest:
            x = load(day, t)
            if x is not None:
                vol = sorted(x["volume"])[len(x) // 2]
                data[t] = [{r[0]: r for r in spikes(x)}, vol]
        h, m = int(hm[:2]), int(hm[3:])
        for shift in range(-5, 6):
            t0 = f"{(h * 60 + m + shift) // 60:02}:{(h * 60 + m + shift) % 60:02}"
            line = f"{t0}           "
            for t in [main] + rest:
                if t in data and t0 in data[t][0]:
                    r = data[t][0][t0]
                    x = r[3] / data[t][1] if data[t][1] > 0 else 0
                    line += f" {r[1]:+5.2f}/{r[2]:+5.2f} {x:3.0f}x"
                else:
                    line += "               -"
            out.write(line + "\n")
        out.write("each cell: went / closed  volume vs normal\n")
    out.close()


def step_rvi():
    # RVI around the spikes: did the "fear index" react, or did the market treat it as a glitch?
    out = open("results/flash/raw/rvi.txt", "w")
    for day, hm, main, rest in cases:
        d = load(day, "RVI")
        if d is None:
            out.write(f"{day}: no RVI\n")
            continue
        c = dict(zip(d["time"], d["close"]))
        before = [x for x in c if x < hm] if hm else []
        after = [x for x in c if hm and x >= hm]
        if not before or not after:
            out.write(f"{day}: RVI has {len(d)} minutes, not enough around {hm}\n")
            continue
        a = c[before[-1]]
        b = max(c[x] for x in after[:10])
        e = c[after[min(30, len(after) - 1)]]
        out.write(f"{day} {hm}: RVI before {a:.2f}, max in 10 min after {b:.2f} ({b - a:+.2f}), 30 min after {e:.2f} ({e - a:+.2f})\n")
    if os.path.exists("data/flash/rvi_daily.csv"):
        r = pandas.read_csv("data/flash/rvi_daily.csv")
        out.write(f"\nRVI daily: {len(r)} days, from {r['date'].iloc[0]} to {r['date'].iloc[-1]}\n")
        r["year"] = r["date"].str[:4]
        for year, g in r.groupby("year"):
            out.write(f"   {year}: mean {g['close'].mean():.1f}, min {g['close'].min():.1f}, max {g['close'].max():.1f}\n")
    out.close()


history = ["USD000UTSTOM", "CNYRUB_TOM", "USDRUBF", "CNYRUBF", "IMOEXF"]


def step_history():
    # full minute history for the detector, one file per instrument per month: data/flash/history/TICKER_YYYY-MM.csv
    # months that already have a file are skipped (the current month is always downloaded again)
    os.makedirs("data/flash/history", exist_ok=True)
    this_month = f"{datetime.now(timezone.utc):%Y-%m}"
    with Client(token) as client:
        for ticker in history:
            uid = ""
            for u in client.instruments.find_instrument(query=ticker).instruments:
                if u.ticker == ticker:
                    uid = u.uid
                    break
            if uid == "":
                print(ticker, "not found")
                continue
            d = datetime(2022, 1, 3, tzinfo=timezone.utc)
            rows = []
            while d < datetime.now(timezone.utc):
                month = f"{d:%Y-%m}"
                path = f"data/flash/history/{ticker}_{month}.csv"
                if os.path.exists(path) and month != this_month:
                    d += timedelta(days=1)
                    continue
                if d.weekday() < 5:
                    time.sleep(0.12)
                    for c in client.market_data.get_candles(from_=d, to=d + timedelta(days=1), interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles:
                        rows.append({"day": f"{c.time:%Y-%m-%d}", "time": f"{c.time:%H:%M}", "open": get_price(c.open), "high": get_price(c.high), "low": get_price(c.low), "close": get_price(c.close), "volume": c.volume})
                nxt = d + timedelta(days=1)
                if f"{nxt:%Y-%m}" != month:
                    pandas.DataFrame(rows, columns=["day", "time", "open", "high", "low", "close", "volume"]).to_csv(path, index=False)
                    print(ticker, month, len(rows), "minutes")
                    rows = []
                d = nxt
            if rows:
                pandas.DataFrame(rows, columns=["day", "time", "open", "high", "low", "close", "volume"]).to_csv(f"data/flash/history/{ticker}_{d - timedelta(days=1):%Y-%m}.csv", index=False)


def step_detect():
    # spike = a minute that went far from the previous close and came back by its close or the next minute's close
    #   far      = at least 0.7% and at least 20x the typical minute move of this instrument in this month
    #   came back = the price is within 1/3 of the jump again
    # real trades only: volume at least 5x the median minute of that day (zero-volume candles are just quotes)
    # open = first 5 minutes of a session (start of the day or after a pause of more than 5 minutes): marked, not mixed with the rest
    # decision = a Bank of Russia decision day, 10:25-11:00 UTC: that's the rate news, not a glitch
    # before = range of the 30 minutes before, in typical minute moves (small = the market was calm)
    out = open("results/flash/raw/detect.txt", "w")
    found = []
    minutes = {}
    for ticker in history:
        files = sorted(f for f in os.listdir("data/flash/history") if f.startswith(ticker + "_") and len(f) == len(ticker) + 12)
        parts = [pandas.read_csv(f"data/flash/history/{f}") for f in files]
        parts = [x for x in parts if len(x) > 0]
        d = pandas.concat(parts, ignore_index=True)
        d["month"] = d["day"].str[:7]
        d["mins"] = d["time"].str[:2].astype(int) * 60 + d["time"].str[3:].astype(int)
        d["prev"] = d.groupby("day")["close"].shift(1)
        d["gap"] = d["mins"] - d.groupby("day")["mins"].shift(1)
        d["next"] = d.groupby("day")["close"].shift(-1)
        d["up"] = (d["high"] / d["prev"] - 1) * 100
        d["down"] = (d["low"] / d["prev"] - 1) * 100
        d["went"] = d["up"].where(d["up"].abs() >= d["down"].abs(), d["down"])
        d["closed"] = (d["close"] / d["prev"] - 1) * 100
        d["closed_next"] = (d["next"] / d["prev"] - 1) * 100
        d["move"] = d["closed"].abs()
        typical = d[d["volume"] > 0].groupby("month")["move"].median()
        d["typical"] = d["month"].map(typical)
        d["vol_x"] = d["volume"] / d.groupby("day")["volume"].transform("median").clip(lower=1)
        start = (d["gap"].isna()) | (d["gap"] > 5)
        d["session"] = start.cumsum()
        d["since_start"] = d.groupby("session").cumcount()
        d["open"] = d["since_start"] < 5
        back = (d["closed"].abs() < d["went"].abs() / 3) | (d["closed_next"].abs() < d["went"].abs() / 3)
        spike = (d["went"].abs() >= 0.7) & (d["went"].abs() >= 20 * d["typical"]) & back & d["prev"].notna() & (d["vol_x"] >= 5)
        hi30 = d.groupby("day")["high"].transform(lambda x: x.shift(1).rolling(30, min_periods=5).max())
        lo30 = d.groupby("day")["low"].transform(lambda x: x.shift(1).rolling(30, min_periods=5).min())
        d["before"] = (hi30 / lo30 - 1) * 100 / d["typical"]
        minutes[ticker] = d.set_index(["day", "time"])[["went", "typical"]]
        for k in d.index[spike]:
            found.append({"ticker": ticker, "day": d["day"][k], "time": d["time"][k], "went": d["went"][k], "closed": d["closed"][k],
                          "closed_next": d["closed_next"][k], "vol_x": d["vol_x"][k], "open": bool(d["open"][k]),
                          "before": d["before"][k], "typical": d["typical"][k]})
        out.write(f"{ticker}: {len(d)} minutes, {d['day'].nunique()} days, typical minute move {d['move'].median():.3f}%\n")

    # did other instruments jump in the same minute? (at least 10x their typical move)
    for f in found:
        others = []
        for t, m in minutes.items():
            if t == f["ticker"] or (f["day"], f["time"]) not in m.index:
                continue
            w, ty = m.loc[(f["day"], f["time"])]
            if abs(w) >= 10 * ty and abs(w) >= 0.2:
                others.append(f"{t} {w:+.1f}")
        f["others"] = ", ".join(others)

    f = pandas.DataFrame(found)
    decisions = set(pandas.read_csv("data/cb_kir_decisions.csv")["date"])
    f["decision"] = f["day"].isin(decisions) & (f["time"] >= "10:25") & (f["time"] <= "11:00")
    f.to_csv("results/flash/raw/spikes.csv", index=False)
    f["year"] = f["day"].str[:4]
    out.write(f"\nspikes found: {len(f)}, of them at the open of a session: {int(f['open'].sum())}\n")
    out.write(f"at a Bank of Russia decision (10:25-11:00 UTC): {int(f['decision'].sum())}\n")
    out.write("2022 is a different market (war, capital controls, almost no yuan trading), so the rest is mostly about 2023-2026\n")
    out.write("\nby instrument and year (not at the open, not at a decision)\n")
    rest = f[~f["open"] & ~f["decision"]]
    out.write(rest.groupby(["ticker", "year"]).size().unstack(fill_value=0).to_string() + "\n")
    out.write("\nby hour UTC (not at the open)\n")
    out.write(rest["time"].str[:2].value_counts().sort_index().to_string() + "\n")
    out.write(f"\nalone (no other instrument jumped): {int((rest['others'] == '').sum())} of {len(rest)}\n")
    out.write(f"market was calm before (30 min range < 10 typical moves): {int((rest['before'] < 10).sum())} of {len(rest)}\n")
    new = rest[rest["day"] >= "2023-01-01"]
    out.write(f"\nsince 2023: {len(new)} spikes, alone: {int((new['others'] == '').sum())}, by hour UTC:\n")
    out.write(new["time"].str[:2].value_counts().sort_index().to_string() + "\n")
    out.write("\nsince 2023, not at the open, not at a decision, biggest first\n")
    out.write(new.sort_values("went", key=abs, ascending=False)[["ticker", "day", "time", "went", "closed", "closed_next", "vol_x", "before", "others"]].round(2).to_string(index=False) + "\n")
    out.write("\n2022, biggest 20\n")
    out.write(rest[rest["day"] < "2023-01-01"].sort_values("went", key=abs, ascending=False).head(20)[["ticker", "day", "time", "went", "closed", "closed_next", "vol_x", "others"]].round(2).to_string(index=False) + "\n")
    out.write("\nat a decision\n")
    out.write(f[f["decision"]][["ticker", "day", "time", "went", "closed", "closed_next", "vol_x", "others"]].round(2).to_string(index=False) + "\n")
    out.write("\nat the open, biggest 20\n")
    out.write(f[f["open"]].sort_values("went", key=abs, ascending=False).head(20)[["ticker", "day", "time", "went", "closed", "closed_next", "vol_x", "others"]].round(2).to_string(index=False) + "\n")
    out.close()


def step_before():
    # was the market thin right before a spike? no order book history, so only signs from candles:
    #   pre volume = volume of the 10 minutes before / normal volume of the same 10 clock minutes on other days of that month
    #   empty      = minutes without trades among those 10
    # placebo = the same clock time on other days of the same month, same instrument (what's normal for that time)
    # spikes since 2023, not at the open, not at a decision
    import random
    random.seed(1)
    f = pandas.read_csv("results/flash/raw/spikes.csv")
    decisions = set(pandas.read_csv("data/cb_kir_decisions.csv")["date"])
    f = f[(f["day"] >= "2023-01-01") & ~f["open"] & ~(f["day"].isin(decisions) & (f["time"] >= "10:25") & (f["time"] <= "11:00"))]

    def window(vol, day, t):
        # volume and empty minutes in the 10 minutes before clock time t
        h, m = int(t[:2]), int(t[3:])
        total = 0
        empty = 0
        for k in range(1, 11):
            x = h * 60 + m - k
            v = vol.get((day, f"{x // 60:02}:{x % 60:02}"), 0)
            total += v
            if v == 0:
                empty += 1
        return total, empty

    out = open("results/flash/raw/before.txt", "w")
    out.write("spikes since 2023 (not at the open, not at a decision). 10 minutes before each spike vs the same clock time on other days of that month\n\n")
    out.write("ticker          spikes | pre volume vs normal (median) | share with < half the normal volume | empty minutes: spikes / placebo\n")
    ratios_all = []
    for ticker in history:
        g = f[f["ticker"] == ticker]
        if len(g) == 0:
            continue
        months = sorted(set(g["day"].str[:7]))
        vol = {}
        days_of = {}
        for mo in months:
            path = f"data/flash/history/{ticker}_{mo}.csv"
            d = pandas.read_csv(path)
            for k in range(len(d)):
                vol[(d["day"][k], d["time"][k])] = d["volume"][k]
            days_of[mo] = sorted(set(d["day"]))
        ratios = []
        empty_s = []
        empty_p = []
        for k in g.index:
            day, t = g["day"][k], g["time"][k]
            v, e = window(vol, day, t)
            others = [x for x in days_of[day[:7]] if x != day]
            normal = sorted(window(vol, x, t)[0] for x in others)
            norm = normal[len(normal) // 2] if normal else 0
            if norm > 0:
                ratios.append(v / norm)
            empty_s.append(e)
            for x in random.sample(others, min(10, len(others))):
                empty_p.append(window(vol, x, t)[1])
        ratios_all += ratios
        ratios.sort()
        med = ratios[len(ratios) // 2] if ratios else float("nan")
        low = sum(1 for r in ratios if r < 0.5)
        out.write(f"{ticker:14} {len(g):6}  |            {med:5.2f}             |        {low:3}/{len(ratios):3}                    |   {sum(empty_s) / len(empty_s):4.1f} / {sum(empty_p) / len(empty_p):4.1f}\n")
    ratios_all.sort()
    out.write(f"\nall: pre volume vs normal, median {ratios_all[len(ratios_all) // 2]:.2f}, below half: {sum(1 for r in ratios_all if r < 0.5)}/{len(ratios_all)}, above 2x: {sum(1 for r in ratios_all if r > 2)}/{len(ratios_all)}\n")
    out.write("by the placebo itself the median is 1 and about a quarter is below half (half of the days are below the median)\n")
    out.close()


def step_cost():
    # 1. cost: how much money traded in the spike minute (lot = 1000 units of currency, so volume x 1000 x price)
    #    IMOEXF only in contracts, its contract size is different
    # 2. shape, to tell a one-off order from a stop hunt:
    #    ladder      = the minute before already went the same way by at least a quarter of the spike
    #    second wave = the next minute traded at least as much as the spike minute (stops and forced closes going off)
    #    after 10 min = price 10 minutes later vs the price before the spike (near 0 = the spike told nothing)
    f = pandas.read_csv("results/flash/raw/spikes.csv")
    decisions = set(pandas.read_csv("data/cb_kir_decisions.csv")["date"])
    f = f[(f["day"] >= "2023-01-01") & ~f["open"] & ~(f["day"].isin(decisions) & (f["time"] >= "10:25") & (f["time"] <= "11:00"))].reset_index(drop=True)
    rows = []
    cache = {}
    for k in range(len(f)):
        t, day, hm = f["ticker"][k], f["day"][k], f["time"][k]
        key = (t, day[:7])
        if key not in cache:
            cache[key] = pandas.read_csv(f"data/flash/history/{t}_{day[:7]}.csv")
        d = cache[key]
        d = d[d["day"] == day].reset_index(drop=True)
        i = d.index[d["time"] == hm][0]
        prev = d["close"][i - 1]
        went = f["went"][k]
        before = d["close"][i - 2] if i >= 2 else prev
        pre_went = pct(before, d["high"][i - 1]) if went > 0 else pct(before, d["low"][i - 1])
        ladder = pre_went * went > 0 and abs(pre_went) >= abs(went) / 4
        second = i + 1 < len(d) and d["volume"][i + 1] >= d["volume"][i]
        later = d["close"][min(i + 10, len(d) - 1)]
        money = d["volume"][i] * 1000 * d["close"][i] / 1e9 if t != "IMOEXF" else None
        rows.append({"ticker": t, "day": day, "time": hm, "went": round(went, 2), "contracts": d["volume"][i],
                     "bn_rub": round(money, 2) if money is not None else None, "ladder": ladder, "second_wave": second,
                     "after_10min": round(pct(prev, later), 2)})
    r = pandas.DataFrame(rows)
    r.to_csv("results/flash/raw/cost.csv", index=False)
    out = open("results/flash/raw/cost.txt", "w")
    out.write("spikes since 2023, not at the open, not at a decision. money = volume of the spike minute x 1000 x price, bn rubles\n\n")
    c = r[r["bn_rub"].notna()]
    out.write(f"currency spikes: {len(c)}, money in the spike minute: median {c['bn_rub'].median():.2f} bn rub, from {c['bn_rub'].min():.2f} to {c['bn_rub'].max():.2f}\n")
    out.write(f"move per 1 bn rub traded (median): {(c['went'].abs() / c['bn_rub']).median():.1f}%\n")
    out.write(f"ladder (the minute before already went that way): {int(r['ladder'].sum())} of {len(r)}\n")
    out.write(f"second wave (next minute traded as much or more): {int(r['second_wave'].sum())} of {len(r)}\n")
    out.write(f"ladder or second wave (stop hunt candidates): {int((r['ladder'] | r['second_wave']).sum())} of {len(r)}\n")
    out.write(f"price 10 minutes later vs before the spike: median |move| {r['after_10min'].abs().median():.2f}%, in the direction of the spike: {int((r['after_10min'] * r['went'] > 0).sum())} of {len(r)}\n")
    out.write("\nall, biggest first\n")
    out.write(r.sort_values("went", key=abs, ascending=False).to_string(index=False) + "\n")
    out.close()


for s in steps:
    globals()[f"step_{s}"]()
