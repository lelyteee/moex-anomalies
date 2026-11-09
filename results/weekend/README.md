# Weekend sessions

Does weekend trading tell anything about Monday?

Weekend stock sessions since 28 Jun 2025, futures since 16 Aug 2025. 52 full weekends.

Raw: [`weekend.txt`](raw/weekend.txt), [`weekend_gap.txt`](raw/weekend_gap.txt), [`morning.txt`](raw/morning.txt)

## Findings

**1. Weekend does not predict Monday.** Same direction in 25/53.

**2. Gap → Monday reversal was an artifact.** Shared open price: corr −0.41. Clean price at 10:05: −0.22, noise.

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

Weak signal. Short IMOEXF Monday 07:00–09:50: +0.10% per trade after costs, mostly from a few big drops.