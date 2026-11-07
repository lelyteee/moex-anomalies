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
changes = pandas.read_csv("data/cb_kir_decisions.csv")


def get_price(x):
    return x.units + x.nano * 1e-9

with Client(token) as client:
    uid = "4821c9aa-36e8-4743-b37c-861e58581b25"
    print(list(CandleInterval))