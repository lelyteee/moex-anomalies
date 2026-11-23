# Methods

Here I explain the stats that my conclusions actually depend on. Basic things (mean, correlation, noise level ±2/√n) are in "How to read" in [key_rate](results/key_rate/). This file is about the less obvious stuff, mostly about how not to fool myself with 27 data points.

## 1. Compare with an ordinary day, not with zero

A 0.7% move means nothing by itself. Some years the market is just more nervous, some minutes are always busy (open, close, start of the hour). So I compare a decision day with the same minutes of ordinary days:

```
ratio = mean |move| on decision days / mean |move| on control days
```

Control day = the same weekday one week earlier, or all ordinary Fridays (all decisions are on Fridays).

Example, IMOEX since Jul 2023: first minute 0.733% vs 0.038% on control days, so 19×. First hour 0.869% vs 0.204%, only 4×. So the big numbers are about the first minute only.

Same with "the reaction grew 15× after 2023": that's first minute only (0.05% → 0.73%). Over the hour it's 2.7× (0.32% → 0.87%).

And with currency: in raw % the dollar moves about 6× less than stocks in the first minute. But the dollar is also calmer on normal days. In its own units the dollar is 5× its normal, stocks are 20×.

## 2. Bootstrap by dates

27 decisions since Jul 2023 is not much, so I want an interval and not just a mean. Bootstrap: take 27 days at random out of my 27, with repeats (some day twice, some day not at all), recompute the number, do it 10 000 times. The middle 95% of the results is the interval. If it doesn't cross zero, good.

The important part is what I resample: whole days. Not minutes, not stocks. Everything that happens on one decision day comes from the same news, so 20 stocks on one day are not 20 independent points, they're basically one. If you count them as 20, t-stats look way better than they are.

I fell for this once. Minute-level detector: 98 jumps at CB announcement times, after the jump the price goes back by 0.44% in 30 minutes, t = −6.3. Looks super strong. But these 98 jumps sit on a few decision days. When I first average the stocks inside each day and then test over the 27 days, the pullback is 0.12% with t = 0.8, i.e. nothing.

## 3. Leave one out

With 27 points one crazy day can make the whole result. 20 Dec 2024 is that day: everyone expected a hike to 23%, the CB kept 21%, the index went +5% in an hour. So I recompute everything dropping each date one by one and look at the worst case.

Example: bonds vs stocks after the decision, corr 0.90. Without 20 Dec 2024 it's 0.70. Bootstrap interval [0.50; 0.98]. So the honest answer is "strong link, somewhere 0.7–0.9", not "0.90".

Also useful here: Spearman correlation. Same as normal correlation but on ranks (biggest day = 27, next = 26, ...), so one huge day can't pull it alone. Here it's 0.74.

## 4. If you pick the best window, you pay for it

I checked if the market keeps going in the direction of the decision day for 1, 3 and 5 days after. 3 days looked best. But if I try 3 windows, the chance that at least one looks good by luck is more than 5%. So the p-value of "the best one" is too optimistic.

Fair way: do exactly the same with random data, including choosing the best window.

1. take 27 random ordinary Fridays
2. compute the 1, 3 and 5 day continuation, keep the best one
3. repeat 20 000 times
4. p = share of random sets where the best was as good as mine or better

Since Jul 2023: p = 0.12% (about 24 out of 20 000). Before Jul 2023: 21%, so nothing there.

## 5. Matched control

Obvious objection: maybe any big day continues the next days, and the CB has nothing to do with it. So for every decision I take ordinary days from the same period where the daily move was about the same size (within ±25%), and compare.

3 days after: decisions +1.03%, ordinary days of the same size +0.11%, difference +0.91%, interval [+0.08; +1.79]. Weaker than without the control, but still above zero.

## 6. Beta vs correlation

Correlation says how tight the link is. Beta says how big. Beta is the slope of the line through the points:

```
beta = cov(stock, index) / var(index)
```

Two stocks can both have corr 0.9 with the index, but one moves 2% when the index moves 1%, and the other 0.5%. Same corr, very different beta.

Example: first hour after a decision, developers (Samolet, LSR) have beta 2.1 to IMOEX, oil and gas 0.88. So a rate decision hits developers about twice as hard as the market. Makes sense, their sales live on mortgage rates.

## 7. Placebo is not zero

When I test "something happens before event X", I don't compare with zero. I run the exact same code on random days of the same stocks (placebo) and compare with that. Random days don't give zero.

Example, dividends: volume in the 3 days before an announcement vs how big the reaction is, corr +0.28. Looks like someone knew. But on random days the same corr is +0.14, just because busy periods stay busy (high volume today, big moves tomorrow). So the part that could be about the announcement is +0.14, not +0.28.

## 8. Normal volume depends on the time of day

Volume on MOEX is high at the open, at the close and at the start of every hour, and low in between. If "normal" is one number for the whole day, the detector keeps firing at the open and the close. So the norm is per minute of the day: what's normal for 07:00 UTC is computed only from 07:00 UTC of other days, separately for each instrument.

The detector flags a minute if it's in the top 0.2% for that instrument both by volume and by price move. With a single daily norm, alarms at the edges of the session were 2× more often.

## 9. Many hypotheses

I checked about 30 ideas. With a 5% threshold 1–2 of them will look significant by pure luck. So results with t around 2 are "maybe". I trust a result more if it also survives 2–5 above and holds in different periods (before and after Jul 2023, or by half-years).

Example: on Wednesdays at 19:00 Moscow (weekly inflation data) the first hour of the evening session moves 1.4× more than on other days since Jul 2023. By half-years: 2.15× in 2024 H2, 0.78× in 2026 H2. So it was a thing for about a year, not a law of nature.
