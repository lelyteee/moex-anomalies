# Before and around the decision

What happens in the week before a Bank of Russia decision, what bonds tell about the reaction, how banks react, and what the press conference adds.

## How to read

- **IMOEX** — stock index. **RGBI** — government bond index. RGBI up = the decision was softer than the market expected, RGBI down = harder. This is our measure of **surprise**: no need to collect analyst forecasts.
- Times are UTC: decision at **10:30 UTC = 13:30 Moscow**, press conference at **12:00 UTC = 15:00 Moscow**.
- **corr** — how often two things move together, from −1 to +1. The **noise level** (about ±0.30–0.39 here) is what random numbers would give.
- **per 1% of IMOEX** — how much a stock moves when the index moves 1%. 1.4 = the stock swings 1.4 times stronger than the market.
- "Not explained by RGBI" — the part of the stock move that the bond surprise does not explain.

| File | What |
|---|---|
| [`index_week.txt`](raw/index_week.txt) | index in the week and the day before each decision |
| [`bonds.txt`](raw/bonds.txt) | bonds vs stocks after the decision, 44 decisions since Apr 2021 |
| [`drift.txt`](raw/drift.txt) | can you earn by following the bond surprise after the first 5 minutes |
| [`banks.txt`](raw/banks.txt) | Sberbank, VTB, T-Technologies, Bank Saint Petersburg, Lukoil (for comparison) |
| [`small_banks.txt`](raw/small_banks.txt) | small and rarely traded banks |
| [`press.txt`](raw/press.txt) | the press conference vs the same time a week earlier |

## Findings

**1. The week before tells nothing.** Neither the index nor bonds in the week before predict the reaction (all correlations inside the noise). The week before looks like any other week; a few big weeks were geopolitics.

**2. Bonds explain the stock reaction.**

| Time after the decision | corr bonds vs stocks | Same direction |
|---|---|---|
| 1 minute | +0.64 | 31 of 44 |
| 5 minutes | +0.67 | 30 of 44 |
| 60 minutes | **+0.86** | 32 of 44 |
| 60 minutes, since Jul 2023 | **+0.90** | 23 of 27 |
| same, without 20 Dec 2024 | +0.70 | |

Softer than expected → stocks up. Harder → stocks down. The surprise decides the direction, not the decision itself.

**3. Why the reaction became 15× bigger in 2023.**

| | before Jul 2023 | since Jul 2023 | × |
|---|---|---|---|
| Size of the surprise (bonds, first hour) | 0.08% | 0.33% | 4 |
| Index move per 1% of bonds | 0.75% | 2.20% | 3 |

The Bank started to surprise more (4×) and stocks started to react more to the same surprise (3×). 4 × 3 ≈ 12–15. The "before" sensitivity is rough: surprises were tiny then.

**4. Rate cuts in 2025–2026.** The index fell on 8 of 10 cut days. In the 6 cuts where bonds fell (the cut was harder than hoped), the index fell every time. Not "buy the rumor, sell the news", but disappointing cuts.

**5. Nothing to earn after the first minutes.** Buying or selling the index at 10:34 in the direction of the bond surprise gave nothing: −0.12% after an hour, +0.07% by the close. The market takes in the surprise within minutes. Weak hint (6 cases): after softer-than-expected decisions the index gave back about 0.6% within the hour.

**6. Banks swing more, but the whole market moves together.** Since Jul 2023, first hour:

| Stock | per 1% of IMOEX | per 1% of bonds | corr with bonds | share of the hour done in the first minute |
|---|---|---|---|---|
| T-Technologies | 1.43 | 3.32 | 0.91 | 100% |
| VTB | 1.35 | 3.08 | 0.88 | 75% |
| Sberbank | 1.10 | 2.49 | 0.90 | 93% |
| Bank Saint Petersburg | 1.00 | 2.21 | 0.81 | 93% |
| IMOEX | 1.00 | 2.20 | 0.90 | 84% |
| Lukoil (for comparison) | 0.74 | 1.60 | 0.79 | 91% |

T-Technologies and VTB react about 1.4× stronger than the index, Lukoil weaker. VTB is the slowest, but too little to trade on.

**7. Moves before the announcement go through the whole market.** The strange 10:29 minutes happen on the same days for every stock:

| Date | Sberbank | VTB | T | BSPB | Lukoil | After |
|---|---|---|---|---|---|---|
| 6 Jun 2025 | −1.14% | −0.31% | −2.40% | −0.33% | −0.43% | up |
| 24 Jul 2026 | +0.34% | +0.35% | +0.39% | +0.36% | +0.31% | up |
| 11 Sep 2026 | +0.73% | +0.86% | +0.87% | +0.34% | +1.19% | down |

On 11 Sep 2026 Lukoil, which cares least about the rate, moved the most. If someone traded on a leak about the rate, banks would move more. Possible explanations: news in that minute (not checked), a big bet on index futures that pulled all stocks, or a leak (least likely: wrong direction on 2 of 3 days).

**8. Small banks.** Since Jul 2023, first hour:

| Bank | Minutes with trades (of 75) | per 1% of IMOEX | corr with bonds |
|---|---|---|---|
| Sovcombank | 75 | 1.40 | 0.89 |
| MTS Bank | 68 | 0.88 | 0.82 |
| MKB | 65 | 1.17 | 0.83 |
| Zaymer | 50 | 0.64 | 0.84 |
| Rosbank | 41 | 0.56 | 0.43 |
| Avangard | 25 | 0.44 | 0.74 |
| Kuznetsky | 22 | 1.23 | 0.48 |

The rarer a stock trades, the weaker and more random its reaction: there are no trades, so the price just stays old. Nothing suspicious before the announcement: 4 bigger moves, two on the market-wide day 11 Sep 2026 and two in the almost dead Avangard and Kuznetsky.

Sovcombank swings the most of all banks (1.39% average move in the first hour), but per unit of surprise it is like T and VTB. The extra swing is its own noise, mostly from 2–3 big drops (26 Jul 2024: −4.95%).

**9. The press conference is a second event.** Average index move since Jul 2023:

| Time (UTC) | Decision day | Same time a week earlier |
|---|---|---|
| 11:29 → 11:59, before it | 0.21% | 0.11% |
| 11:59 → 12:30 | **0.33%** | 0.10% |
| 11:59 → 13:00 | 0.44% | 0.19% |
| 13:00 → close | 0.51% | 0.43% |

Before Jul 2023 there was no difference. The press conference explains most of the days where the end of the day was far from the first hour: 6 Jun 2025 (+0.51% in the first hour, then −1.11% during the press conference), 13 Sep 2024 (−1.45%, then +1.16%), 24 Jul 2026 (+1.46%). Bonds move with stocks during it, but weaker (corr +0.48): the market reacts to words about the future. The first hour does not tell where the press conference will go.

**10. Key meetings vs regular ones.** Four times a year (Feb, Apr, Jul, Oct, plus 15 Sep 2023) the Bank also publishes a new forecast, including where the rate is going in the next years.

| Since Jul 2023 | Key (15) | Regular (12) |
|---|---|---|
| index move, first hour | 0.65% | 1.15% |
| bond surprise | 0.28% | 0.39% |
| corr bonds vs stocks | +0.63 | **+0.96** |
| move not explained by bonds | 0.43% | 0.32% |

On regular meetings bonds explain the stock reaction almost completely. On key meetings much worse: part of the surprise is in the forecast, and the bond index catches it badly. 15 Sep 2023, when stocks went most against bonds (+0.78% while bonds −0.40%), was a key meeting.
