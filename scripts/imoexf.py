from t_tech.invest import Client
from t_tech.invest import CandleInterval
from datetime import datetime, timezone
from t_tech.invest.schemas import CandleSource
import time
import pandas

import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

def get_price(x):
    return x.units + x.nano * 1e-9

with Client(token) as client:
    c = client.instruments.find_instrument(query="IMOEXF")
    for u in c.instruments:
        print(u.name, u.ticker, u.class_code, u.uid, u.first_1day_candle_date)
    fut = "5bcff194-f10d-4314-b9ee-56b7fdb344fd"  # IMOEXF
    idx = "4821c9aa-36e8-4743-b37c-861e58581b25"  # IMOEX
    changes = pandas.read_csv("data/cb_kir_decisions.csv")
    out = open("results/imoexf.txt", "w")
    for k in range(len(changes)):
        day = changes["date"][k]
        if day < "2023-11-14":
            continue
        date = datetime.strptime(day, "%Y-%m-%d")
        start = date.replace(hour=10, minute=14, tzinfo=timezone.utc)
        end = date.replace(hour=10, minute=46, tzinfo=timezone.utc)
        f = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=fut, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        x = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_1_MIN, instrument_id=idx, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        index = {}
        for c in x:
            index[c.time] = c

        normal = []
        for c in f:
            if 15 <= c.time.minute <= 24:  # normal volume = mean of 10:15-10:24
                normal.append(c.volume)
        normal = sum(normal) / len(normal) if len(normal) > 0 else 0

        rb = changes["rate_before"][k]
        ra = changes["rate_after"][k]
        out.write(f"{day}   {rb} -> {ra} ({ra - rb:+})\n")
        out.write("time  |  index close      %  |    fut close      %     volume   vol x\n")
        prev_i = -1
        prev_f = -1
        for c in f:
            t = c.time
            fc = get_price(c.close)
            if prev_f == -1:
                prev_f = get_price(c.open)
            fp = (fc - prev_f) / prev_f * 100
            prev_f = fc
            if t in index:
                ic = get_price(index[t].close)
                if prev_i == -1:
                    prev_i = get_price(index[t].open)
                ip = (ic - prev_i) / prev_i * 100
                prev_i = ic
                s_i = f"{ic:11.2f} {ip:+6.2f}%"
            else:
                s_i = " " * 19
            vx = c.volume / normal if normal > 0 else 0
            if t.minute == 14:
                continue
            out.write(f"{t.hour:02}:{t.minute:02} | {s_i} | {fc:11.2f} {fp:+6.2f}% {c.volume:10} {vx:6.1f}\n")
        out.write("\n")
    out.close()

    # 5-second candles, 10:15-10:45 UTC, index and IMOEXF. T-Invest keeps them only for the last 30 days
    sec = open("results/imoexf_seconds.txt", "w")
    today = datetime.now(timezone.utc)
    for k in range(len(changes)):
        day = changes["date"][k]
        date = datetime.strptime(day, "%Y-%m-%d")
        start = date.replace(hour=10, minute=15, tzinfo=timezone.utc)
        end = date.replace(hour=10, minute=45, tzinfo=timezone.utc)
        if (today - start).days >= 30:
            continue
        f = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_5_SEC, instrument_id=fut, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        x = client.market_data.get_candles(from_=start, to=end, interval=CandleInterval.CANDLE_INTERVAL_5_SEC, instrument_id=idx, candle_source_type=CandleSource.CANDLE_SOURCE_EXCHANGE).candles
        index = {}
        for c in x:
            index[c.time] = get_price(c.close)
        rb = changes["rate_before"][k]
        ra = changes["rate_after"][k]
        sec.write(f"{day}   {rb} -> {ra} ({ra - rb:+})\n")
        sec.write("time      |  index close      %  |    fut close      %   volume\n")
        prev_i = -1
        prev_f = -1
        for c in f:
            t = c.time
            fc = get_price(c.close)
            if prev_f == -1:
                prev_f = get_price(c.open)
            fp = (fc - prev_f) / prev_f * 100
            prev_f = fc
            if t in index:
                ic = index[t]
                if prev_i == -1:
                    prev_i = ic
                ip = (ic - prev_i) / prev_i * 100
                prev_i = ic
                s_i = f"{ic:11.2f} {ip:+6.3f}%"
            else:
                s_i = " " * 20
            sec.write(f"{t.hour:02}:{t.minute:02}:{t.second:02}  | {s_i} | {fc:11.2f} {fp:+6.3f}% {c.volume:8}\n")
        sec.write("\n")
    sec.close()
