# Key rate decisions

How IMOEX moves when the Bank of Russia announces the key rate.

## Summary

- **Is there a jump?** Yes. Since mid-2023 the index moves 0.5–2% within the first minute after the release, and the move usually does not reverse within an hour (one exception: 15 Aug 2023).
- **Where?** The decision alone does not tell. A hike can push the index up or down. Examples suggest the direction follows the surprise relative to expectations. Not tested yet: analyst consensus is still missing.
- **When?** Since mid-2023 the reaction is about 15× larger than in 2021 – mid-2023.
- **Why from 2023?** Likely two conditions at once: the market became sensitive to the rate (capital locked inside the country, retail-driven trading, credit dependence), and the rate became high and uncertain (hiking cycle from Aug 2023). A high rate alone was not enough: in spring 2022 the rate was 11–20%, the Bank cut it by 3 p.p. twice at extraordinary meetings, and the reaction stayed near zero. The first strong reaction is the extraordinary hike of 15 Aug 2023. Hypothesis, not proven.
- **Anything suspicious?** In 4 days the index moved 0.4–1.2% in the minutes *before* the release, confirmed on futures. In two of them the move went the same way as the later reaction. Under check.

## Setup

Raw output: [`results_2.txt`](raw/results_2.txt) (forward windows), [`results_1.txt`](raw/results_1.txt) (±x windows, old), [`around_1030.txt`](raw/around_1030.txt) (candles 10:25–10:35).

## Findings

**1. The decision itself does not set the direction.**

| Decision | Days | Index down at +1 min | Up |
|---|---|---|---|
| Hike | 15 | 10 | 5 |
| Hold | 16 | 8 | 8 |
| Cut | 14 | 7 | 7 |

**2. Two regimes.** Since mid-2023 the reaction is roughly 15× larger.

| Period | Days | mean \|+1 min\| | mean \|+5 min\| | mean \|to close\| |
|---|---|---|---|---|
| Mar 2021 – Jun 2023 | 18 | 0.05% | 0.13% | 0.53% |
| Jul 2023 – Oct 2026 | 27 | 0.73% | 0.83% | 1.59% |

The new regime starts with the extraordinary decision of 15 Aug 2023 (8.5% → 12%), which also opened the hiking cycle. See finding 8.

**3. The move happens in the first minute and holds.** In all 18 scheduled days with \|+5 min\| ≥ 0.5%, the sign at +60 min is the same. The one clear reversal is the extraordinary decision of 15 Aug 2023 (finding 8).

**4. Expectations matter more than the decision.**

- 20 Dec 2024 — rate held at 21% while a hike was expected: +2.0% in one minute, +7.8% to close
- 19 Jun 2026 and 24 Jul 2026 — both −0.25 p.p.: −1.6% and +1.5% at +1 min

**5. Unusual moves one minute before the release.** Typical move inside the 10:29 candle: 0.025% (median).

| Date | Decision | 10:29 (before) | +1 min (after) |
|---|---|---|---|
| 6 Jun 2025 | 21 → 20 | −1.15% | +2.03% |
| 11 Sep 2026 | 14 → 14 | +0.94% | −0.69% |
| 24 Jul 2026 | 14.25 → 14 | +0.44% | +1.47% |

Not verified yet. Possible causes: release a few seconds early, timestamp shift in the data, another event, trading before the release.

**6. Reaction starts within 5 seconds.** 5-second candles exist only for the last 30 days, so only 23 Oct 2026 can be checked.

| Time (UTC) | Price | Comment |
|---|---|---|
| 10:29:55 | 2433.84 | last price before the release |
| 10:30:00–05 | low 2425.16 | −0.36% in the first 5 seconds |
| 10:30:35 | 2418.26 | bottom, −0.64% |

The release came out exactly at 10:30:00 and T-Invest timestamps are accurate for this day. The minute before was calm: the largest 5-second move was +0.13% at 10:29:25, then back. The three suspicious days are older than 30 days and cannot be checked this way.

Futures on the same day ([`imoexf_seconds.txt`](raw/imoexf_seconds.txt)): trading jumps exactly at 10:29:00, from ~50 to ~1,000 contracts per 5 seconds, and stays high for the whole minute (about 16,000 contracts in 10:29). The largest burst, 5,126 contracts at 10:29:25, lifted the price by 0.19% and it came back within 10 seconds. Net move over the minute: −0.04%. The release itself brought 50,449 contracts in the first 5 seconds. So heavy volume at 10:29 alone looks like normal two-sided positioning before the release, not a sign of a leak. A price move before the release is what matters.

**7. Futures confirm the pre-release moves.** IMOEXF. Raw: [`imoexf.txt`](raw/imoexf.txt).

- In the three suspicious days the futures moved the same way as the index at 10:29, so these are real trades, not a data error.
- Volume is shown relative to the mean of 10:15–10:24 on the same day.

| Date | Decision | Pre-release move | Volume × normal | Reaction 10:30 | Same direction? |
|---|---|---|---|---|---|
| 13 Sep 2024 | 18 → 19 | 10:25, −0.42% | 5.8 | −1.00% | yes |
| 6 Jun 2025 | 21 → 20 | 10:29, −1.16% | 18.2 | +2.03% | no |
| 24 Jul 2026 | 14.25 → 14 | 10:26, +0.83% | 12.6 | +1.47% | yes |
| 11 Sep 2026 | 14 → 14 | 10:29, +0.94% | 36.9 | −0.69% | no |

- In the other 20 days the index moved less than 0.2% in any minute before the release.
- Two days had heavy volume at 10:29 without a price move: 24 Oct 2025 (17.7×) and 23 Oct 2026 (25.4×).
- Opposite-direction cases look like bets on the expected decision rather than leaks. Same-direction cases are worth checking against news.
- IMOEXF volume grew from ~10 contracts per minute in Dec 2023 to 600–3,500 in 2025–2026. Volume ratios before mid-2024 are not reliable. This growth reflects the new instrument getting popular, not the whole market.

**8. Extraordinary decisions.** Release times from the Bank of Russia file names and news timestamps. 28 Feb 2022 (9.5 → 20) is skipped: the stock market was closed.

| Date | Decision | Release (UTC) | Release minute | Next 45 min |
|---|---|---|---|---|
| 8 Apr 2022 | 20 → 17 | 08:40 | −0.03% | slow drift, −0.4% |
| 26 May 2022 | 14 → 11 | 07:30 (approx.) | −0.06% | slow drift, +0.5% |
| 15 Aug 2023 | 8.5 → 12 | 07:30 | **−0.82%** | reversal: +1.2% above the pre-release level by 07:58 |

- Even 3 p.p. cuts in 2022 did not move the market. Before mid-2023 extraordinary meetings did not change the picture.
- 15 Aug 2023 is the first strong reaction in the whole sample and the start of the new regime.
- It is also the only clear reversal: −0.8% in the first minute, then up. Two of these meetings (26 May 2022 and 15 Aug 2023) were announced a day before, so the direction was expected and only the size was a surprise.

## Discussion

Comments from an economist (informal):

- **Why reactions grew.** After 2022 companies lost access to foreign capital and depend on domestic credit and the state. The key rate became the main channel, so the market is more sensitive to it.
- **Expectations.** Prices already include the expected decision. When the rate does not change, credit conditions do not change either, so a strong move on a hold day can only come from expectations.
- **10:29 moves** may partly be expectations being realized just before the release.

Another view (informal discussion):

- After 2022 foreign companies sold their Russian businesses to local owners, often on credit. Capital stayed inside the country, foreign investment stopped. About a year into the war the market accepted that this is long-term, and sentiment changed. Together this made the market more dependent on domestic credit and on the key rate.

Reaction vs rate level (mean \|+1 min\|):

| Rate before decision | Days | mean \|+1 min\| |
|---|---|---|
| below 10% | 17 | 0.05% |
| 10–17% | 17 | 0.61% |
| 17% and above | 11 | 0.85% |

Rate level and time overlap: the rate was below 10% only before Aug 2023. One exception helps: in spring 2022 the rate was high (17% on 29 Apr, 11% on 10 Jun), yet the reaction was tiny (0.07% and 0.04%). The extraordinary cuts of 8 Apr 2022 (20 → 17) and 26 May 2022 (14 → 11) also passed almost unnoticed. So a high rate alone is not enough. The switch in Aug 2023 needs both a high, uncertain rate and a market that became sensitive to it.

Open points:

- The timing does not fully fit the first argument: reactions stayed small through the second half of 2022 and only grew from mid-2023, together with the hiking cycle. Dependence on the rate explains *why* the market reacts, but not *why from 2023*.
- Expectations are priced over days, not in one minute. A 1% move inside the minute before the release still needs a trigger.

## Notes and ideas

Personal takeaways, not verified.

- **News first.** Any unusual move has to be checked against news and company disclosures before calling it an anomaly. A move right after a news item is a reaction, not an anomaly.
- **Look at single stocks, not the index.** Pump-and-dump schemes and insider trading are said to be common on the Russian market, mostly in low-liquidity stocks where little money moves the price. The index averages this away.
- **Spike and reversal.** A sharp move followed by a quick move back is the hard case: it can be a stop-hunt, a manipulation or a liquidity shock. In this sample: 6 Jun 2025, 11 Sep 2026 (before the release) and 15 Aug 2023 (after). A simple first detector: a jump above X% within a minute, then more than half of it given back within N minutes.
- **Insider footprint.** Someone with inside information may take a large, often leveraged position in a stock nobody usually trades. Open data does not show who traded or with what leverage, only the footprint: volume many times above the stock's norm, then a disclosure, then a price move in the same direction. False positives matter: count how often a volume spike is followed by news at all.
- **Labelled examples.** The Bank of Russia publishes cases of detected market manipulation and insider trading. If they include tickers and dates, they could serve as known examples to test a detector on.
- **Related work.** Bernile, Hu, Tang (2016) found informed trading in S&P 500 futures in the minutes before Fed announcements — the closest analogue to the moves before 10:30 here.
