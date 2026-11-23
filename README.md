# moex-anomalies

Research on anomalies and possible manipulation in Moscow Exchange equities.
AI360, HSE University.

## Goals

Build a pipeline that detects unusual trading activity on MOEX and study what follows it.

- Unusual daily and hourly volumes
- Large buys and sells, with and without a later price reversal
- Detection methods: statistical thresholds, Isolation Forest, Local Outlier Factor

## Research questions

- Do signs of insider trading appear before material disclosures?
- Are there sharp moves or squeezes around key rate decisions?
- Are low-liquidity stocks more exposed to manipulation?
- How does the price behave after an anomaly, and over what horizon?

## Current work

| Topic | What | Status |
|---|---|---|
| [key_rate](results/key_rate/) | how IMOEX reacts to Bank of Russia decisions, minute by minute | done, updating |
| [pre_decision](results/pre_decision/) | week and morning before the decision, bonds as a surprise measure, banks | done, updating |
| [after_decision](results/after_decision/) | does the move continue for days after the decision | soon |
| [cpi_wednesday](results/cpi_wednesday/) | weekly inflation data on Wednesday evenings | soon |
| [stocks](results/stocks/) | single stocks: pumps, dividends, strange minutes | soon |

Also coming:

- **Currency.** Dollar, yuan and gold on decision days react much weaker than stocks. I thought the link to the surprise disappeared after 2023, but before 2023 there are only 6–11 days and one day flips the result, so I can't say that.
- **One-minute spikes.** On 21 Jul 2022 at 10:12 Moscow the dollar, yuan and both currency futures jumped 3.5–4% in one minute and mostly came back in the next one, stocks dipped at the same time. I found no news for that minute. Such spikes happen on MOEX every now and then, I want to find all of them and see what comes before.
- **High and low around 10:30.** What happens inside the first minutes, not only the close.
- **Every new decision.** I collect minute and 5-second data for each meeting, next one is 18 Dec 2026.

## What holds so far

I rechecked the main results with separate code and stricter controls.

- **Holds.** Since mid-2023 the reaction to the key rate is much bigger and almost instant: in 2025–2026 the first minute is about 90% of the first hour.
- **Holds, but smaller.** Bonds and stocks move together after the decision, corr somewhere 0.7–0.9, not one clean number: 20 Dec 2024 alone does a lot of it.
- **Nothing found.** No sign that someone trades in the right direction before 10:30. Volume before the release goes up, but it doesn't guess where the price goes.
- **Didn't hold.** "The press conference sets the direction for the next days" and "the ruble stopped reacting to the rate after 2023". Both looked nice, both were too weak.

How I compute things and why (bootstrap, controls, placebo etc): [`METHODS.md`](METHODS.md)

## Structure

```
scripts/key_rate.py           index: download candles, compute reactions
scripts/imoexf.py             IMOEXF futures: price, volume, 5-second candles
scripts/decision.py           around the decision: daily data, extraordinary meetings, week before,
                              bonds, drift, banks, small banks, press conference, minute candles,
                              high / low at 10:30, currency, after the decision (pick steps at the top)
scripts/collect.py            raw 5-second candles for the last ~30 days (T-Invest doesn't keep more)
data/instruments.csv          all instruments: ticker, name, kind, uid
data/cb_kir_decisions.csv     decision dates, rate before / after
data/imoex_daily.csv          IMOEX daily candles since 2021
data/banks.csv                banks and Lukoil: tickers and uids
results/key_rate/             reaction to the decision
results/pre_decision/         week before, bonds, banks, press conference
results/after_decision/       days after the decision (soon)
results/cpi_wednesday/        weekly inflation on Wednesdays (soon)
results/stocks/               single stocks (soon)
```

## Run

```bash
pip install pandas python-dotenv t-tech-investments
echo "T_INVEST_TOKEN=..." > .env   # read-only token
python scripts/key_rate.py
python scripts/decision.py   # steps at the top of the file
```

