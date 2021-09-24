import logging
import pandas as pd
import os
import datetime as dt

## Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] (%(asctime)s)  %(message)s"
)
my_logger = logging.getLogger("my_logger")


header_dict = {
    "净值日期": "Date",
    "单位净值": "NAV",
    "累计净值": "Accm NAV",
    "日增长率": "Day%Chg",
    "申购状态": "申购状态",#"Purchase",
    "赎回状态": "赎回状态",#"Redemption",
    "分红送配": "Dividend",
}

def str2date(_input:str):
    # return dt.datetime.strptime(_input, "%Y-%m-%d")
    return dt.date.fromisoformat(_input)

def get_another_day(date, duration):
    return date - dt.timedelta(days=duration)


