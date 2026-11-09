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
