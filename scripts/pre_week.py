import pandas

def pct(a, b):
    return (b - a) / a * 100

def corr(a, b):
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    c = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    return c / (va * vb) ** 0.5

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
