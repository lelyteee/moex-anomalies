# Before and around the decision

What happens in the week before a Bank of Russia decision, and what bonds say about the reaction.

| File | What |
|---|---|
| [`index_week.txt`](raw/index_week.txt) | IMOEX, week and day before each decision, 45 decisions |
| [`bonds.txt`](raw/bonds.txt) | RGBI (government bond index) vs IMOEX after 10:30 UTC, 44 decisions from Apr 2021 |
| [`drift.txt`](raw/drift.txt) | IMOEX after 10:34 in the direction of the bond surprise, 27 decisions from Jul 2023 |
| [`banks.txt`](raw/banks.txt) | SBER, VTBR, T, BSPB, LKOH (control) vs IMOEX and RGBI, 46 decisions |
| [`small_banks.txt`](raw/small_banks.txt) | smaller and illiquid banks, 46 decisions |

RGBI up = yields down = the decision was softer than expected. RGBI minute data from Apr 2021; no RGBI daily data in T-Invest before Sep 2023, so the bond week-before move covers 26 decisions.

## Findings

**1. The week before tells nothing.** Index week before → reaction: corr −0.04 (+1 min), −0.18 (+60 min). Bonds week before → reaction: +0.32, 0.00. Noise ±0.30–0.39. Week-before mean +0.64% vs −0.06% for any week, but up only 23/45: a few big geopolitical weeks.

**2. Bonds explain the stock reaction.**

| Window | corr RGBI vs IMOEX | Same direction |
|---|---|---|
| +1 min | +0.64 | 31/44 |
| +5 min | +0.67 | 30/44 |
| +60 min | +0.86 | 32/44 |
| Jul 2023 – Oct 2026, +60 min | +0.90 | 23/27 |
| same, without 20 Dec 2024 | +0.70 | |

Softer than expected → stocks up, harder → stocks down. The surprise sets the direction, measured without analyst consensus.

**3. Why the reaction grew ~15× in 2023.**

| | Before Jul 2023 | From Jul 2023 | × |
|---|---|---|---|
| Surprise, mean \|RGBI +60 min\| | 0.08% | 0.33% | 4 |
| IMOEX per 1% of RGBI, +60 min | 0.75% | 2.20% | 3 |

Surprises became ~4× larger and stocks ~3× more sensitive to the same surprise. The old-regime sensitivity is rough: surprises there were tiny.

**4. Cuts in 2025–2026.** IMOEX fell on 8 of 10 cut days. In the 6 cuts where bonds fell (harder than expected), the index fell every time. Not "sell the news", but cuts that disappointed.

**5. No drift after the first minutes.** Trading IMOEX from 10:34 in the direction of the bond surprise: −0.12% to 11:29 (12/27 wins), +0.07% to close (16/27). The market prices the surprise within minutes. Hint, 6 cases only: after softer-than-expected decisions the index gave back −0.56% within the hour.

**6. Banks are more sensitive, the whole market moves together.**

| From Jul 2023, +60 min | per 1% IMOEX | per 1% RGBI | corr with RGBI | +1 min share of +60 |
|---|---|---|---|---|
| T | 1.43 | 3.32 | 0.91 | 1.02 |
| VTBR | 1.35 | 3.08 | 0.88 | 0.75 |
| SBER | 1.10 | 2.49 | 0.90 | 0.93 |
| BSPB | 1.00 | 2.21 | 0.81 | 0.93 |
| IMOEX | 1.00 | 2.20 | 0.90 | 0.84 |
| LKOH (control) | 0.74 | 1.60 | 0.79 | 0.91 |

Bank minus IMOEX from +5 to +60 in the direction of the surprise: −0.30% to +0.11%, noise. VTBR is the slowest, but too little to trade.

**7. Moves before the release are market-wide.** The unusual 10:29 minutes fall on the same days for every stock:

| Date | SBER | VTBR | T | BSPB | LKOH | After |
|---|---|---|---|---|---|---|
| 6 Jun 2025 | −1.14% | −0.31% | −2.40% | −0.33% | −0.43% | up |
| 24 Jul 2026 | +0.34% | +0.35% | +0.39% | +0.36% | +0.31% | up |
| 11 Sep 2026 | +0.73% | +0.86% | +0.87% | +0.34% | +1.19% | down |

On 11 Sep 2026 Lukoil, the least rate-sensitive stock, moved the most. Banks do not stand out, so this does not look like a leak about the rate. Open versions:

- a news item in that minute (not checked);
- a large position in index futures before the release, with arbitrage pulling all index stocks;
- a leak (weakest: wrong direction in 2 of 3 days, banks not ahead).

**8. Small and illiquid banks.** From Jul 2023, +60 min.

| Stock | Minutes with trades (of 75) | per 1% IMOEX | corr with RGBI |
|---|---|---|---|
| SVCB | 75 | 1.40 | 0.89 |
| MBNK | 68 | 0.88 | 0.82 |
| CBOM | 65 | 1.17 | 0.83 |
| ZAYM | 50 | 0.64 | 0.84 |
| ROSB | 41 | 0.56 | 0.43 |
| AVAN | 25 | 0.44 | 0.74 |
| KUZB | 22 | 1.23 | 0.48 |

The less a stock trades, the weaker and noisier its reaction within the hour: prices are stale. Before the release only 4 big moves (≥0.5%) in all small banks: two on 11 Sep 2026 (the market-wide day), two in illiquid AVAN and KUZB on 9 Jun 2023. Only one went the same way as the reaction. Nothing suspicious here.
