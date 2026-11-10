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

**Key rate decisions** — how IMOEX reacts to Bank of Russia announcements, minute by minute.
Results: [`results/key_rate/`](results/key_rate/)

**Before and around the decision** — week before, and government bonds as a surprise measure.
Results: [`results/pre_decision/`](results/pre_decision/)

**Volume spikes** — what happens to a stock after a day of 5×+ volume, by liquidity tier.
Results: [`results/stocks/`](results/stocks/)

## Structure

```
scripts/key_rate.py           index: download candles, compute reactions
scripts/imoexf.py             IMOEXF futures: price, volume, 5-second candles
scripts/decision.py           around the decision: daily data, extraordinary meetings, week before,
                              bonds, drift, banks, small banks, press conference (pick steps at the top)
scripts/stocks.py             all shares: liquidity tiers, volume spikes (pick steps at the top)
data/cb_kir_decisions.csv     decision dates, rate before / after
data/imoex_daily.csv          IMOEX daily candles since 2021
data/banks.csv                banks and Lukoil: tickers and uids
data/stocks.csv               all TQBR shares with liquidity tiers
results/key_rate/             reaction to the decision
results/pre_decision/         week before, bonds, banks, press conference
results/stocks/               volume spikes by liquidity tier
```

## Run

```bash
pip install pandas python-dotenv t-tech-investments
echo "T_INVEST_TOKEN=..." > .env   # read-only token
python scripts/key_rate.py
python scripts/decision.py   # steps at the top of the file
python scripts/stocks.py
```

