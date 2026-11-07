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
Results: [`results/key_rate.md`](results/key_rate.md)

## Structure

```
scripts/key_rate.py           download candles, compute reactions
data/cb_kir_decisions.csv     decision dates, rate before / after
results/key_rate.md           findings
results/*.txt                 raw output
```

## Run

```bash
pip install pandas python-dotenv t-tech-investments
echo "T_INVEST_TOKEN=..." > .env   # read-only token
python scripts/key_rate.py
```

