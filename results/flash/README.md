# One-minute spikes

The price jumps a few percent inside one minute and comes back in the same or the next minute. On MOEX it happens every now and then and gets into the news. Is it random glitches, or is there a pattern: where, when, what comes before?

Raw: [`cases.txt`](raw/cases.txt), [`rvi.txt`](raw/rvi.txt), `scripts/flash.py`. Times UTC. "Went" = how far the minute went from the previous close (high or low), "closed" = where the minute closed.

## Known cases

| Date, minute | Instrument | Went | Closed | Volume vs normal minute | The rest |
|---|---|---|---|---|---|
| 21 Jul 2022, 07:12 | dollar | +3.10% | +1.52% | 8× | yuan +2.9%, dollar futures +3.4% (34×): the whole currency market |
| 19 Aug 2022, 07:00 | dollar | −3.27% | −0.57% | 9× | yuan −1.6%. First minute of the session |
| 16 Jan 2024, 14:06 | dollar | **+5.60%** | +2.00% | 146× | yuan +1.7%, futures only +0.7% |
| 9 Feb 2024, 11:15 | dollar | +2.97% | +0.15% | 86× | yuan +0.05%, futures +0.37%: only the dollar |
| 9 Jun 2025, 08:29 | dollar futures (Jun) | **−7.85%** | −0.15% | 100× | perpetual dollar futures −0.2%, yuan nothing |
| 16 Sep 2025, 08:33 | index futures (Sep) | −5.47% | −0.19% | 102× | IMOEXF −0.88%, index −0.29%, 2 days before expiry |
| 24 Oct 2025, 10:29 | IMOEXF | +0.62% | +0.04% | 50× | the whole stock market, 1 minute before the rate decision |
| 25 Aug 2023 | dollar "today" | | | | not in T-Invest; dollar "tomorrow" didn't spike, only volume 109× at 14:30 |

What they have in common: one minute, volume 50–150× normal, and the price is mostly back by the end of the same minute.

Two kinds:
- **One instrument.** 9 Feb 2024, 9 Jun 2025, 16 Sep 2025: only one thing jumps, its neighbours barely move. Looks like one big market order into a thin order book. Two of them are quarterly futures, one 2 days before expiry, when most traders already moved to the next contract.
- **The whole market.** 21 Jul 2022, 16 Jan 2024, 24 Oct 2025: several instruments jump together. That's not a typo in one order, someone moved everything at once, or there was news I didn't find.

Stocks don't care about currency spikes: IMOEX moves less than 0.1% in those minutes (only 21 Jul 2022 −0.3%).

## RVI

RVI is the "fear index" of the Russian market, like VIX: it's built from option prices and shows how big a move the market expects. Minute RVI in T-Invest exists only from 2025. During 16 Sep 2025 it went +0.8 and back, on 24 Oct 2025 it didn't move. So the option market treated these spikes as glitches, not as real news.

RVI by year (daily close): 2021 27.5, 2022 60.6, 2023 29.9, 2024 28.8, 2025 38.5, 2026 31.0. The reaction to the key rate grew a lot since 2023 while the market overall was calmer than in 2022. So the bigger reaction is not just general nervousness.

## Detector

The news only shows the cases someone noticed. So I took every minute since Jan 2022 for the dollar and yuan (spot and perpetual futures) and IMOEXF, 3.4 million minutes, step `detect`, raw: [`detect.txt`](raw/detect.txt), list: [`spikes.csv`](raw/spikes.csv).

A spike = a minute that went at least 0.7% and at least 20× the typical minute of this instrument in this month, came back within a third of the jump by its close or the next minute's close, with volume at least 5× the median minute of the day. The first 5 minutes of every session and 10:25–11:00 on decision days are counted separately: the first is the normal mess at the open, the second is the rate news.

It finds the known ones (21 Jul 2022, 16 Jan 2024, 9 Feb 2024, the index futures on 16 Sep 2025). It doesn't see 9 Jun 2025 and 25 Aug 2023 because those were in instruments I don't have (quarterly futures, dollar "today").

2022 is a different market (war, capital controls, the yuan was barely traded): 337 spikes, mostly in the yuan. Since 2023: **89 spikes on 63 days**, about one a month, 13 of them 2% or more. 50 of the 89 are alone, no other instrument jumped. 60 came back already by the close of the same minute.

Biggest since 2023 that I didn't see in the news:

| Date, minute UTC | Instrument | Went | Closed | Volume vs normal |
|---|---|---|---|---|
| 28 Apr 2026, 06:04 | dollar futures | **−8.26%** | −0.23% | 109× |
| 30 Jun 2023, 06:28 | dollar futures | +7.24% | +0.28% | 184× |
| 21 Nov 2023, 07:54 | yuan futures | +4.70% | +0.04% | 528× |
| 16 Dec 2024, 07:09 | dollar futures | −3.42% | −0.18% | 87× |
| 12 Aug 2024, 18:41 | dollar futures | −2.76% | −0.21% | 52× |
| 8 Jan 2024, 07:01 | IMOEXF | +2.75% | +0.53% | 93× |

When: 30 in the morning (06:00–07:59 UTC, the first hours of trading), 25 in the evening session (16:00+), 33 in the rest of the day. The morning and the evening are short and thin, so they get more spikes per hour than the middle of the day.

## Was the market thin right before?

I have no order book history, only candles. So: volume in the 10 minutes before each spike vs the same clock time on other days of that month, and minutes without any trade. Step `before`, raw: [`before.txt`](raw/before.txt).

I expected an empty market before the spike. It's the opposite:

| | spikes | normal for that time |
|---|---|---|
| volume in the 10 minutes before | **3.9×** normal (median) | 1× by definition |
| below half the normal volume | 7 of 89 | about a quarter |
| minutes without trades (of 10) | 0–1.4 | 0–2.3 |

So spikes don't come out of a dead market. They come when the market is already busy, something is going on, and then one more big order eats the book. It looks like the 2010 Flash Crash in the US: it happened on a nervous, busy day, when liquidity ran out, not when nobody was trading. Careful though: days with spikes are probably news days, so part of the "busy" is just the news.

## How much it costs, and who wins

Money that traded in the spike minute (volume × 1000 × price, a lot is 1000 units of currency). Step `cost`, raw: [`cost.txt`](raw/cost.txt), [`cost.csv`](raw/cost.csv).

- Median spike minute: **0.5 bn rubles**. Dollar futures −8.3% on 28 Apr 2026: 1.1 bn. The biggest, dollar spot +5.6% on 16 Jan 2024: 13 bn.
- That's the whole minute, not one player, others trade in it too. So in a thin minute moving the dollar by a few % takes less than a billion rubles. For a big bank or a fund that's not much. The anomaly is really holes in liquidity.
- 10 minutes later the price is about where it was before (median 0.19%). The spike tells nothing about where the price goes.

Who wins and who loses: whoever hit the book with a market order sold at 68.6 instead of 74.8 (28 Apr 2026), about 6 mln rubles lost per 1 mln dollars filled like that. Whoever had limit orders deep in the book bought cheap and could sell back a minute later. Three stories fit this:

1. **Fat finger.** A wrong-sized market order by mistake. No scheme, someone just lost money.
2. **Stop hunt.** Someone pushes the price on purpose so other people's stop orders and forced closes of leveraged positions go off, and buys back at the bottom. Then the spike should come in steps.
3. **A broken robot** on a thin market.

Candles can't tell these apart, but they can show the steps. Ladder = the minute before already went the same way, second wave = the next minute traded as much or more. **25 of 89** spikes have one of the two. The four biggest futures spikes all come in two minutes: 30 Jun 2023 +2.4%, then +7.2%; 28 Apr 2026 −8.3%, then the next minute traded twice as much; 21 Nov 2023 yuan +4.7%, then +2.5% with 4× the volume; 12 Aug 2024 −2.8%, then −1.9%. Those are the best stop hunt candidates. The big spot spikes (16 Jan 2024, 9 Feb 2024) are one minute, closer to one big order.

Who did it and why can't be seen in public data, only the exchange and the Bank of Russia see who sent the orders. What I can say: the anomaly is regular (about once a month), it's cheap, and the way money moves in it is clear.

## Next

- Same detector on stocks, especially the illiquid ones.
- 5-second data: `collect.py` now saves currency too, so the next spike within a month can be seen at 5 seconds.
