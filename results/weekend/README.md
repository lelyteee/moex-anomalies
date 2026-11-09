# Weekend sessions

Does weekend trading tell anything about Monday?

Weekend stock sessions since 28 Jun 2025, futures since 16 Aug 2025.

| File | Sample |
|---|---|
| [`weekend.txt`](raw/weekend.txt) | first rough pass, 56 weekends incl. 2 working Saturdays and 1 broken day |
| [`weekend_gap.txt`](raw/weekend_gap.txt) | 52 weekends with full Saturday and Sunday sessions |
| [`morning.txt`](raw/morning.txt) | all weekdays since 18 Aug 2025: 64 Mondays, 248 other days |

IMOEXF morning window: 09:00–09:50 MSK until 13 Jul 2026, 07:00–09:50 MSK from 14 Jul 2026 (futures morning session moved).

## Findings

**1. Weekend does not predict Monday.** Same direction in 28/52, corr −0.19 (noise ±0.28).

**2. Gap → Monday reversal was an artifact.** First pass, shared open price: corr −0.41. Clean price at 10:05: −0.22, noise.

**3. Monday morning → main session: outliers.** Corr −0.45, without 18 Jul 2026 −0.27.

**4. Monday mornings fall.**

| | Mean | Up | t |
|---|---|---|---|
| Weekend, IMOEX2 | +0.16% | 37/52 | +1.9 |
| Monday morning, IMOEX2 | −0.23% | 19/52 | −3.3 |
| Monday morning, IMOEXF | −0.14% | 22/64 | −2.2 |
| Tue–Fri mornings, IMOEXF | +0.01% | 126/248 | +0.5 |

But: without the 3 largest Mondays −0.06%.

## Verdict

Weak signal. Short IMOEXF in the Monday morning session until 09:50 MSK: +0.10% per trade after costs, mostly from a few big drops.