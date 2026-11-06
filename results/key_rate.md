# Key rate decisions

How IMOEX moves when the Bank of Russia announces the key rate.

## Setup

- IMOEX, 1-minute exchange candles, T-Invest API
- 46 scheduled decisions, Mar 2021 – Oct 2026 (45 with data; 18 Mar 2022 — market closed)
- Release at 10:30 UTC
- Reference price: close of the 10:29 candle
- Extraordinary decisions not included yet

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

## Limitations

- 45 events: small sample
- No analyst consensus yet, so surprise is not measured
- No comparison with the same minute on ordinary days
- Index only: no volume