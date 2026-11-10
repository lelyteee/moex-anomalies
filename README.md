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

## Structure

```
scripts/key_rate.py           index: download candles, compute reactions
scripts/imoexf.py             IMOEXF futures: price, volume, 5-second candles
scripts/extra.py              extraordinary decisions
scripts/pre_decision.py       daily IMOEX, bond index and bank lookups
scripts/pre_week.py           week before each decision
scripts/bonds.py              bond index (RGBI) vs IMOEX around the release
scripts/drift.py              IMOEX after the first minutes vs bond surprise
scripts/banks.py              banks and Lukoil around the release
data/cb_kir_decisions.csv     decision dates, rate before / after
data/imoex_daily.csv          IMOEX daily candles since 2021
data/banks.csv                banks and Lukoil: tickers and uids
results/key_rate/README.md    findings
results/key_rate/raw/         raw output (txt tables)
results/pre_decision/         week before, bonds, banks
```

## Run

```bash
pip install pandas python-dotenv t-tech-investments
echo "T_INVEST_TOKEN=..." > .env   # read-only token
python scripts/key_rate.py
```

