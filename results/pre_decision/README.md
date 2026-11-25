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

How solid is 0.90 ([`bonds_check.txt`](raw/bonds_check.txt), step `bonds_check`): bootstrap by dates gives [0.50; 0.98], without 20 Dec 2024 it's 0.70, rank corr 0.74. So the link is strong, but 0.90 is the optimistic end.

And there's a catch. The first minute of IMOEX predicts where RGBI goes over the next hour (corr +0.70), the other way it doesn't work (−0.44). RGBI is built from weighted average prices, so it's slow and partly just follows stocks. It's a good hint about the surprise, but not a clean outside measure of it.

**3. Why the reaction became 15× bigger in 2023.**

| | before Jul 2023 | since Jul 2023 | × |
|---|---|---|---|
| Size of the surprise (bonds, first hour) | 0.08% | 0.33% | 4 |
| Index move per 1% of bonds | 0.75% | 2.20% | 3 |

The Bank started to surprise more (4×) and stocks started to react more to the same surprise (3×). 4 × 3 ≈ 12–15. But after the catch in finding 2 I don't trust this split: if RGBI partly follows stocks, "bigger surprise" and "more sensitive" get mixed. The "before" sensitivity is also rough, surprises were tiny then. To split it properly I need a surprise measure that doesn't depend on stocks, like analyst consensus.

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

On regular meetings bonds explain the stock reaction almost completely. On key meetings much worse: part of the surprise is in the forecast, and the bond index catches it badly. But it's only 15 vs 12 meetings: a random split of the same meetings gives the same or bigger difference in 29% of cases, so this is an idea, not a result. 15 Sep 2023, when stocks went most against bonds (+0.78% while bonds −0.40%), was a key meeting.

**11. News on the strange days.** Days where stocks moved far from what bonds explain, checked against the news:

| Date | Decision | What the news says | Fits |
|---|---|---|---|
| 24 Oct 2025 (key) | cut 17 → 16.5% | the Bank raised its average rate forecast for 2026 to 13–15% (was 12–13%); analysts called it more negative than the cut itself. Two days earlier the US sanctioned Rosneft and Lukoil | first the cut (+0.96%), then the forecast (−1.42% in an hour). The surprise was in the forecast, as in finding 10 |
| 15 Dec 2023 | hike 15 → 16% | the Bank hinted the hiking cycle may be over. Same day: Sovcombank IPO, Lukoil dividend gap at the open | soft signal → stocks above what bonds say |
| 11 Sep 2026 | hold at 14% | 23 of 30 economists expected a hold, yet the index fell about 1%. The media also saw a short jump at about 13:20 Moscow (2295 → 2317) before the release | the market priced a cut more than economists did: analyst surveys miss what the market expects, bonds catch it |
| 24 Jul 2026 | cut 14.25 → 14% | most analysts expected a hold; the index fell more than 2% before the decision, then +1.06% at 13:30 | an unexpected cut, normal reaction |
| 15 Sep 2023 (key) | hike 12 → 13% | hike of 100 bp was mostly expected; the Bank said more hikes were possible; the US sanctioned 150+ companies the same day | not explained: stocks +0.78% while bonds −0.40% |

Sources: [Moscow Times 24.10.2025](https://ru.themoscowtimes.com/2025/10/24/obobschenie-tsbr-ponizil-stavku-do-1650-povysiv-ee-traektoriyu-na-sleduyuschiy-god-a178296), [Investfuture 15.12.2023](https://investfuture.ru/articles/stavka-16-ts-b-tushit-pozhar-v-ekonomike-lukoyl-uronil-rynok-moschniy-start-sovkombanka-novosti), [Vedomosti 11.09.2026](https://www.vedomosti.ru/investments/news/2026/09/11/1228155-indeks-snizilsya), [Kommersant 24.07.2026](https://www.kommersant.ru/doc/8843967), [Prime 24.07.2026](https://1prime.ru/20260724/aktsii-871749704.html), [Investfuture 15.09.2023](https://investfuture.ru/articles/ts-b-povysil-stavku-chto-dalshe-otskok-mosbirzhi-novye-sanktsii-i-zoloto-na-kolyme-novosti).

**12. Developers don't move before the release.** If someone knew the decision, developers would be the best place to trade it: after the release they move about 2× the index (here developers minus IMOEX after 10:30 goes with IMOEX at corr +0.90). And they get less attention than the futures. So I checked: does Samolet, LSR, Etalon, Glorax (average) minus IMOEX before 10:30 go the way the market goes after? Raw: [`dev_leak.txt`](raw/dev_leak.txt), step `dev_leak`.

| Since Jul 2023, 27 decisions | corr with IMOEX after | same direction | control days corr |
|---|---|---|---|
| morning 07:00–10:29 | −0.28 | 11 of 27 | +0.13 |
| 10:00–10:29 | −0.12 | 13 of 27 | −0.04 |
| 10:24–10:29 | −0.29 | 9 of 27 | +0.29 |

All inside the noise (±0.38), and if anything the wrong way. In the last 5 minutes developers move more than usual relative to the index (0.17% vs 0.07% on control days), but in random directions. So more trading before the release, no knowledge, same as with the index and banks.

**13. No "pre-FOMC drift" here.** In the US stocks rise in the day before Fed decisions (Lucca and Moench, 2015), it's a known anomaly. The first runs here said IMOEX rises in the morning before a decision too. Checked against the control day of each meeting. Raw: [`morning_check.txt`](raw/morning_check.txt), step `morning_check`.

| Since Jul 2023, 26 pairs | decision | up | control | difference, 95% |
|---|---|---|---|---|
| previous close → 10:29 | +0.24% | 19 of 26 | +0.24% | +0.00 [−0.51; +0.51] |
| 07:00 → 10:29 | +0.19% | 20 of 26 | −0.00% | +0.20 [−0.10; +0.50] |
| 07:00 → 08:30 | +0.12% | 16 of 26 | −0.01% | +0.14 [−0.11; +0.37] |
| 08:30 → 10:29 | +0.07% | 14 of 26 | +0.01% | +0.06 [−0.24; +0.35] |

The morning goes up on 20 of 26 decision days, but against its own control day the difference includes zero. And over the whole time from the previous close it's exactly the same as the control: the morning rise just makes up for a weaker night. The morning also doesn't guess where the market goes after the release (corr +0.23, same sign 11 of 26, noise ±0.39). So it's at most a weak "maybe", not an anomaly.

**14. Fear before the decision.** In the US the option market expects bigger moves before a Fed decision and calms down right after. Here with RVI (the "fear index", from option prices), daily closes, change in % of the RVI level, vs all other Fridays. Raw: [`rvi.txt`](raw/rvi.txt), step `rvi`.

| Since Jul 2023, 27 decisions | decision | other Fridays | difference, 95% | RVI went down |
|---|---|---|---|---|
| 5 sessions before | +2.98% | −0.01% | +3.00 [−1.73; +8.18] | 10 of 27 |
| the decision day | −1.04% | −0.02% | −1.02 [−3.56; +1.62] | 18 of 27 |
| the day after | +4.25% | +2.94% | +1.32 [−1.95; +5.04] | 4 of 27 |

The shape is the US one: fear goes up in the days before, down on the day itself in 18 of 27 meetings. But every interval includes zero, and before Jul 2023 it was the other way (−3.9% in the 5 sessions before). The day after is a Monday, and RVI goes up on Mondays anyway. So the option market barely prices the meeting in advance.
