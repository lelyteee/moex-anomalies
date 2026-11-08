from t_tech.invest import Client
from t_tech.invest import CandleInterval
from datetime import datetime, timezone, timedelta
from t_tech.invest.schemas import CandleSource
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

def get_price(x):
    return x.units + x.nano * 1e-9

# extraordinary decisions: date, release time UTC, rate before, rate after
# 28.02.2022 (9.5 -> 20) is skipped: stock market was closed
extra = [
    ["2022-04-08", 8, 40, 20.0, 17.0],   # cbr file 08042022_114000key -> 11:40 MSK
    ["2022-05-26", 7, 30, 14.0, 11.0],   # interfax 10:33 MSK, release ~10:30 MSK (check on candles)
    ["2023-08-15", 7, 30, 8.5, 12.0],    # cbr file 15082023_103000Key -> 10:30 MSK
]

with Client(token) as client:
    uid = "4821c9aa-36e8-4743-b37c-861e58581b25"
    for day, h, m, rb, ra in extra:
        date = datetime.strptime(day, "%Y-%m-%d")
        news = date.replace(hour=h, minute=m, tzinfo=timezone.utc)
        start = news - timedelta(minutes=16)
        end = news + timedelta(minutes=46)
        candles = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=uid, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        print(f"{day}   {rb} -> {ra} ({ra - rb:+})   release {h:02}:{m:02} UTC   ({len(candles)} candles)")
        print("time  |    open    close      %")
        prev = -1
        for c in candles:
            t = c.time
            o = get_price(c.open)
            cl = get_price(c.close)
            if prev == -1:
                prev = o
            p = (cl - prev) / prev * 100
            prev = cl
            mark = "  <- release" if t == news else ""
            print(f"{t.hour:02}:{t.minute:02} | {o:8.2f} {cl:8.2f} {p:+6.2f}%{mark}")
        print()
