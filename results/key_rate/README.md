# Key rate decisions

What happens to the Russian stock market in the minutes when the Bank of Russia announces the key rate.

## How to read

- **IMOEX** — Moscow Exchange index, the average of the largest Russian stocks. **IMOEXF** — a futures contract on it: same price, but it is actually traded, so it has volume.
- **RGBI** — index of Russian government bonds. Bonds rise when the market expects lower rates. So after a decision: RGBI up = the decision was softer than expected, RGBI down = harder.
- Times are UTC. The decision is published at **10:30 UTC = 13:30 Moscow**. "+1 min", "+60 min" — price change from the last price before 10:30.
- **mean |x|** — average size of a move, ignoring its direction.
- **corr** — correlation, from −1 to +1: how often two things move together. Near 0 = no link. With few data points random numbers also give a non-zero correlation; the **noise level** (about 2 ÷ √number of points, ±0.30 for 45 decisions) shows what luck alone can give.
- **Surprise** — the difference between the decision and what the market expected.

## Summary

- **Is there a jump?** Yes. Since mid-2023 the index moves 0.5–2% in the first minute after the decision. Usually the move then holds for at least an hour.
- **Which way?** The decision alone does not tell: a rate hike can push the market up or down. What decides is the surprise. When bonds rise after the decision, stocks rise; when bonds fall, stocks fall (corr +0.86 over 44 decisions, see [pre_decision](../pre_decision/)).
- **Since when?** Before mid-2023 the market barely reacted. Since then the first minute is about 15× bigger than before (0.05% → 0.73%), but the first hour only about 2.5×. Compared with an ordinary day, the first minute now moves about 19× more, the hour about 4×.
- **Faster every year.** In 2021–2022 the first minute was a tiny part of the hourly move. In 2025–2026 it's about 90% of it. The market prices the decision almost instantly now.
- **Why?** Not clear yet. I first split it on bonds: surprises about 4× bigger, stocks about 3× more sensitive. But RGBI is slow (it's built from weighted average prices) and partly follows stocks, so it can't split it like that.
- **Anything suspicious?** On 4 days the market moved 0.4–1.2% in the minutes *before* the announcement. Checked on futures: these were real trades. Not explained yet.

Raw data: [`results_2.txt`](raw/results_2.txt) (moves after 10:29), [`results_1.txt`](raw/results_1.txt) (first version, windows around 10:30), [`around_1030.txt`](raw/around_1030.txt) (every minute 10:25–10:35).

## Findings

**1. The decision itself does not set the direction.** Index in the first minute:

| Decision | Days | Down | Up |
|---|---|---|---|
| Hike | 15 | 10 | 5 |
| Hold | 16 | 8 | 8 |
| Cut | 14 | 7 | 7 |

**2. Two periods.** Average size of the index move:

| Period | Days | first minute | first 5 min | to the end of the day |
|---|---|---|---|---|
| Mar 2021 – Jun 2023 | 18 | 0.05% | 0.13% | 0.53% |
| Jul 2023 – Oct 2026 | 27 | 0.73% | 0.83% | 1.59% |

But I shouldn't compare with zero, ordinary days also move. Same minutes on the control day (same weekday a week earlier), decision day divided by control day. Raw: [`faster.txt`](raw/faster.txt), code: step `faster` in `decision.py`.

| Period | Days | 1 min | 10 min | 1 hour | to the close |
|---|---|---|---|---|---|
| Mar 2021 – Jun 2023 | 18 | 1.4× | 2.3× | 1.9× | 1.0× |
| Jul 2023 – Oct 2026 | 26 | 18.7× | 12.0× | 4.1× | 2.7× |

So "15× bigger" is true only for the first minute. Over the hour the reaction grew about 2.5× (0.34% → 0.85%), to the close about 3× (0.51% → 1.57%). The 95% intervals (bootstrap by dates, see [METHODS](../../METHODS.md)) are in the raw file, since Jul 2023 none of them gets close to 1.

The new period starts with the emergency decision of 15 Aug 2023 (8.5% → 12%, after the ruble fell below 100 per dollar). See finding 8.

**3. The move happens in the first minute and holds.** In all 18 regular meetings with a move of 0.5% or more in the first 5 minutes, the market was still on the same side an hour later. The only clear U-turn is 15 Aug 2023.

And it gets faster every year. Share = (1 min move) / (1 hour move), median over the decisions of the year. Same sign = the first minute and the hour went the same way.

| Year | Days | Share | Same sign |
|---|---|---|---|
| 2021 | 7 | −0.02 | 3/7 |
| 2022 | 7 | 0.10 | 5/7 |
| 2023 | 8 | 0.24 | 5/8 |
| 2024 | 8 | 0.45 | 6/8 |
| 2025 | 8 | 0.92 | 6/8 |
| 2026 | 7 | 0.87 | 7/7 |

In 2021 the first minute said nothing about the hour. In 2026 it's almost the whole hour and the direction matched 7 of 7. My guess is algos that read the release and trade within seconds, but minute candles can't show that. 5-second data from the next decisions should.

**4. Expectations matter more than the decision.**

- 20 Dec 2024: the market expected a hike, the rate was kept at 21%. Index +2.0% in one minute, +7.8% by the end of the day.
- 19 Jun 2026 and 24 Jul 2026: the same decision, −0.25 p.p. Reactions in the first minute: −1.6% and +1.5%.

**5. Strange moves one minute before the announcement.** Usually the index barely moves in the minute 10:29 (typical move 0.025%). Three exceptions:

| Date | Decision | 10:29, before | first minute after |
|---|---|---|---|
| 6 Jun 2025 | 21 → 20 | −1.15% | +2.03% |
| 11 Sep 2026 | 14 → 14 | +0.94% | −0.69% |
| 24 Jul 2026 | 14.25 → 14 | +0.44% | +1.47% |

Possible reasons: the release came out a few seconds early, wrong timestamps in the data, other news in that minute, or trading by someone who knew in advance.

**6. The reaction starts within 5 seconds.** 5-second data is kept only for 30 days, so only 23 Oct 2026 could be checked.

| Time (UTC) | Index | Comment |
|---|---|---|
| 10:29:55 | 2433.84 | last price before |
| 10:30:00–05 | low 2425.16 | −0.36% in the first 5 seconds |
| 10:30:35 | 2418.26 | bottom, −0.64% |

The release came out exactly at 10:30:00, the timestamps are correct. The minute before was calm: one +0.13% jump at 10:29:25 that came back in 10 seconds.

Futures that day ([`imoexf_seconds.txt`](raw/imoexf_seconds.txt)): trading jumps at exactly 10:29:00, from about 50 to 1,000 contracts per 5 seconds, and stays high for the whole minute. Price did not move overall (−0.04%). The announcement itself brought 50,449 contracts in the first 5 seconds. So heavy trading in the minute before is normal: people take positions both ways. What matters is a price move before the announcement, not volume.

**7. Futures confirm the moves before the announcement.** Raw: [`imoexf.txt`](raw/imoexf.txt). Volume = how many times above the normal level of 10:15–10:24 the same day.

| Date | Decision | Move before | Volume | Move after | Same direction? |
|---|---|---|---|---|---|
| 13 Sep 2024 | 18 → 19 | 10:25, −0.42% | 5.8× | −1.00% | yes |
| 6 Jun 2025 | 21 → 20 | 10:29, −1.16% | 18.2× | +2.03% | no |
| 24 Jul 2026 | 14.25 → 14 | 10:26, +0.83% | 12.6× | +1.47% | yes |
| 11 Sep 2026 | 14 → 14 | 10:29, +0.94% | 36.9× | −0.69% | no |

- On the other 20 days with futures data the index moved less than 0.2% in any minute before the announcement.
- Moves in the wrong direction look like bets on the expected decision that failed, not leaks. Moves in the right direction are worth checking against news.
- Futures volume grew from about 10 to 600–3,500 contracts per minute between Dec 2023 and 2025–2026: the instrument became popular. Volume comparisons before mid-2024 are not reliable.

**8. Emergency (unscheduled) decisions.** 28 Feb 2022 (9.5 → 20) is skipped: the stock market was closed.

| Date | Decision | Announced (UTC) | First minute | Next 45 minutes |
|---|---|---|---|---|
| 8 Apr 2022 | 20 → 17 | 08:40 | −0.03% | slow drift, −0.4% |
| 26 May 2022 | 14 → 11 | about 07:30 | −0.06% | slow drift, +0.5% |
| 15 Aug 2023 | 8.5 → 12 | 07:30 | **−0.82%** | U-turn: +1.2% above the start by 07:58 |

- Even 3 p.p. cuts in 2022 did not move the market. Bonds barely moved either: the cuts were expected.
- 15 Aug 2023 is the first strong reaction in the whole data and the start of the new period.

**9. What close hides: high and low.** Every minute has a high and a low, not only a close. Raw: [`highlow_check.txt`](raw/highlow_check.txt), step `highlow_check` in `decision.py`. Since Jul 2023, decision days vs the same weekday a week earlier.

Inside the minute 10:30 the price swings a lot: high − low is 12–38× an ordinary day (IMOEX 0.87% vs 0.05%, Samolet 3.9% vs 0.1%).

But it doesn't overshoot. The part of the move that comes back by the end of the minute is 15–32%, about the same as for any big minute on an ordinary day (9–34%). So at 10:30 the price jumps to the new level, it doesn't fly past it and come back.

Before the release it's different. Minutes in 10:25–10:29 where the price went 0.3% or more and came back inside the same minute: 17 on decision days, 0 on control days. Most of them are Samolet in random directions, it's a thin and jumpy stock. But one day stands out:

| 24 Oct 2025, minute 10:29 | went | closed | 10:30 after |
|---|---|---|---|
| IMOEXF | +0.62% | +0.04% | +1.07% |
| Lukoil | +0.62% | +0.02% | +0.55% |
| IMOEX | +0.46% | +0.09% | +0.97% |
| T | +0.46% | +0.01% | +1.04% |
| Sberbank | +0.40% | +0.12% | +1.41% |
| Gazprom | +0.31% | +0.03% | +0.99% |

The whole market jumped up and came back within one minute right before the release, and then went up for real. By closes this minute looks flat, that's why it's not in finding 5. Same kind of thing as the dollar spike on 21 Jul 2022, only here it's right before a decision. With minute candles I can't see what happened inside, 5-second data and the live record on the next meetings should show it.

## Why the market became so sensitive

Opinions from conversations, not proven:

- **Economist 1.** After 2022 companies lost foreign money and depend on Russian loans and the state. The key rate became the main lever, so the market reacts to it more.
- **Economist 1.** Prices already include the expected decision. If the rate does not change, loans do not change either, so a big move on such a day can only come from expectations.
- **Economist 1.** The moves at 10:29 may partly be expectations playing out just before the announcement.
- **Economist 2.** The moves at 10:29 may be an ordinary market action or a change in market structure, not an anomaly. Compare with the S&P 500 around US Federal Reserve decisions.
- **Another view.** After 2022 foreign companies sold their Russian businesses to local owners, often with loans. Money got stuck inside the country. About a year into the war the market accepted that this is long-term, and the mood changed.

What the data says:

| Rate before the decision | Days | average move, first minute |
|---|---|---|
| below 10% | 17 | 0.05% |
| 10–17% | 17 | 0.61% |
| 17% and above | 11 | 0.85% |

A higher rate goes with bigger reactions, but the rate was below 10% only before Aug 2023, so this mixes with time. In spring 2022 the rate was high (17% and 11%) and the reaction was tiny: bonds barely moved, those decisions were expected. Bonds give the answer: since 2023 surprises are about 4× bigger and stocks about 3× more sensitive ([pre_decision](../pre_decision/)).

Still open: the first explanation says *why* the market reacts, but not *why exactly from 2023*. And expectations build up over days, so a 1% move in the minute before the announcement still needs a reason.

## Ideas

Own thoughts, not checked.

- **News first.** Any strange move must be checked against news before calling it an anomaly.
- **Single stocks, not the index.** Pumps and insider trading are said to be common on the Russian market, mostly in small stocks where little money moves the price. The index averages this away. See [stocks](../stocks/).
- **Jump and fall back.** A sharp move that quickly reverses can be a manipulation, someone hunting stop orders, or just a lack of buyers. A simple detector: a jump of more than X% in a minute, then more than half of it back within N minutes.
- **Insider footprint.** Someone with inside information may buy a lot of a stock nobody usually trades, often with borrowed money. We cannot see who traded, only the footprint: volume many times above normal, then news, then a price move the same way. Also count how often such a spike is *not* followed by news.
- **Known cases.** The Bank of Russia publishes cases of proven manipulation and insider trading. They could be used to test a detector.
- **Similar research.** Bernile, Hu, Tang (2016) found informed trading in S&P 500 futures in the minutes before US Federal Reserve announcements — the closest analogue to the moves before 10:30 here.
