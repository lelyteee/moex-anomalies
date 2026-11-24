# Sectors

Who reacts to the key rate the most. This is the "normal" reaction for each kind of stock: if one stock on a decision day goes far from what its sector usually does, that's where to look for something strange.

Raw: [`sectors.txt`](raw/sectors.txt), step `sectors` in `decision.py`. First hour after the release (10:29 → 11:29 UTC), since Jul 2023. Beta = how much the group moves when IMOEX moves 1% (slope, see [METHODS](../../METHODS.md)). Control = the same weekday a week earlier.

| Group | Beta on decision days | Beta on control days | Difference, 95% |
|---|---|---|---|
| Developers (Samolet, LSR, Etalon, Glorax) | **2.11** | 1.26 | +0.86 [+0.43; +1.37] |
| Big banks (Sber, VTB, T) | 1.30 | 0.90 | +0.40 [+0.13; +0.63] |
| Mid banks (BSPB, Sovcombank, MTS Bank, MKB) | 1.13 | 0.87 | +0.26 [−0.27; +0.79] |
| Retail (X5, Magnit) | 1.20 | 1.46 | −0.26 [−1.26; +0.35] |
| Aeroflot | 1.69 | 1.54 | +0.15 [−0.41; +0.58] |
| Oil and gas (Lukoil, Rosneft, Gazprom) | 0.87 | 0.85 | +0.02 [−0.23; +0.21] |

- **Developers** move about 2× the index when the rate comes out, on an ordinary day about 1.3×. Their sales live on mortgages and their debt on the key rate, so it makes sense. Samolet 2.4, LSR 2.5, Etalon 1.6.
- **Big banks** also get more sensitive on decision days (1.3 vs 0.9), less than developers.
- **Oil and gas** don't care: same beta as on any day, below 1. Their money is in dollars and oil, not in the rate.
- Retail, Aeroflot and mid banks: no clear difference, intervals too wide.

I hoped that developers minus oil and gas would be a cleaner "rate only" measure than the index. On decision days it goes with bonds at corr +0.85, but with IMOEX itself at +0.92, so here it's basically the index times a number. It could still help on days when the market moves for other reasons (sanctions, oil), I haven't checked that.
