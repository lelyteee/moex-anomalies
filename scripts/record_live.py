# Records every trade (with side: buy or sell) and the top of the order book, live.
# Run on a decision day from the morning and keep it running (Ctrl-C to stop): python scripts/record_live.py
# Output: data/live/DATE_trades.csv and data/live/DATE_book.csv, times UTC. direction 1 = buy, 2 = sell
from t_tech.invest import Client, MarketDataRequest
from t_tech.invest import SubscribeTradesRequest, TradeInstrument
from t_tech.invest import SubscribeOrderBookRequest, OrderBookInstrument
from t_tech.invest import SubscriptionAction
from datetime import datetime, timezone
import time
import pandas

import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ["T_INVEST_TOKEN"]

tickers = ["IMOEXF", "RGBIF", "USDRUBF", "SBER", "VTBR", "T", "SMLT", "LKOH"]
instruments = pandas.read_csv("data/instruments.csv", dtype=str)
uids = {}
for k in range(len(instruments)):
    if instruments["ticker"][k] in tickers:
        uids[instruments["uid"][k]] = instruments["ticker"][k]


def get_price(x):
    return x.units + x.nano * 1e-9


def requests():
    yield MarketDataRequest(subscribe_trades_request=SubscribeTradesRequest(
        subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
        instruments=[TradeInstrument(instrument_id=u) for u in uids]))
    yield MarketDataRequest(subscribe_order_book_request=SubscribeOrderBookRequest(
        subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
        instruments=[OrderBookInstrument(instrument_id=u, depth=10) for u in uids]))
    while True:
        time.sleep(1)


os.makedirs("data/live", exist_ok=True)
today = f"{datetime.now(timezone.utc):%Y-%m-%d}"
trades = open(f"data/live/{today}_trades.csv", "a")
book = open(f"data/live/{today}_book.csv", "a")
if trades.tell() == 0:
    trades.write("time,ticker,direction,price,quantity\n")
if book.tell() == 0:
    book.write("time,ticker,bid1,bid1_size,ask1,ask1_size,bid_size_10,ask_size_10\n")

while True:
    try:
        with Client(token) as client:
            for m in client.market_data_stream.market_data_stream(requests()):
                if m.trade is not None:
                    t = m.trade
                    # direction: 1 = покупка (покупатель взял заявку продавца), 2 = продажа
                    trades.write(f"{t.time:%Y-%m-%d %H:%M:%S.%f},{uids.get(t.instrument_uid, t.figi)},{int(t.direction)},{get_price(t.price)},{t.quantity}\n")
                    trades.flush()
                if m.orderbook is not None:
                    b = m.orderbook
                    if len(b.bids) > 0 and len(b.asks) > 0:
                        book.write(f"{b.time:%Y-%m-%d %H:%M:%S.%f},{uids.get(b.instrument_uid, b.figi)},{get_price(b.bids[0].price)},{b.bids[0].quantity},{get_price(b.asks[0].price)},{b.asks[0].quantity},{sum(x.quantity for x in b.bids)},{sum(x.quantity for x in b.asks)}\n")
                        book.flush()
    except KeyboardInterrupt:
        break
    except Exception as e:
        # связь оборвалась: ждём 2 секунды и подключаемся снова
        print(datetime.now(), "reconnect:", str(e)[:100])
        time.sleep(2)
trades.close()
book.close()
