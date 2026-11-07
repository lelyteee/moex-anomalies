# Key rate decisions

How IMOEX moves when the Bank of Russia announces the key rate.

## Summary

- **Is there a jump?** Yes. Since mid-2023 the index moves 0.5–2% within the first minute after the release, and the move does not reverse within an hour.
- **Where?** The decision alone does not tell. A hike can push the index up or down. Examples suggest the direction follows the surprise relative to expectations. Not tested yet: analyst consensus is still missing.
- **When?** Since mid-2023 the reaction is about 15× larger than in 2021 – mid-2023.
- **Anything suspicious?** In 3 of 45 days the index moved 0.4–1.2% in the minute *before* the release. Under check.

## Setup

Raw output: [`results_2.txt`](results_2.txt) (forward windows), [`results_1.txt`](results_1.txt) (±x windows, old), [`around_1030.txt`](around_1030.txt) (candles 10:25–10:35).

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

The new regime starts with 15 Sep 2023. The hiking cycle itself started a month earlier, with the extraordinary decision of 15 Aug 2023 (8.5% → 12%).

**3. The move happens in the first minute and holds.** In all 18 days with \|+5 min\| ≥ 0.5%, the sign at +60 min is the same.

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

## Discussion

Comments from an economist (informal):

- **Why reactions grew.** After 2022 companies lost access to foreign capital and depend on domestic credit and the state. The key rate became the main channel, so the market is more sensitive to it.
- **Expectations.** Prices already include the expected decision. When the rate does not change, credit conditions do not change either, so a strong move on a hold day can only come from expectations.
- **10:29 moves** may partly be expectations being realized just before the release.

Open points:

- The timing does not fully fit the first argument: reactions stayed small through the second half of 2022 and only grew from mid-2023, together with the hiking cycle. Dependence on the rate explains *why* the market reacts, but not *why from 2023*.
- Expectations are priced over days, not in one minute. A 1% move inside the minute before the release still needs a trigger.
