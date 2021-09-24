import pandas as pd
import requests
import datetime as dt
from bs4 import BeautifulSoup
import numpy as np
from utils import my_logger, header_dict
from utils import str2date, get_another_day
import argparse
import json
import re
import os


def get_all_funds(save_filepath="./data/funds.txt"):
    url = "http://fund.eastmoney.com/js/fundcode_search.js"
    rsp = requests.get(url)
    all_funds_txt = rsp.text
    all_funds_txt = all_funds_txt[all_funds_txt.find('=')+2:all_funds_txt.rfind(';')]
    try:
        with open(save_filepath, "w") as f:
            f.write(all_funds_txt)
    except FileNotFoundError:
        my_logger.warning("Cannot save file {}".format(save_filepath))
    # all_funds_list = json.loads(all_funds_txt)
    # my_logger.info("\n{}".format(all_funds_list[:10]))
    my_logger.info("Get all funds successfully.")
    return json.loads(all_funds_txt)

def get_fund_info(fund_code="000051", info_op=2, filepath="./data/funds.txt"):
    ## info_op = [fund_code, fund_name_EN_brief, fund_name_CN, fund_type, fund_name_EN]
    try:
        with open(filepath, "r") as f:
            all_funds_list = json.loads(f.read())
    except FileNotFoundError:
        all_funds_list = get_all_funds(filepath)
    for it_fund in all_funds_list:
        if it_fund[0] == fund_code:
            return it_fund[info_op]
    my_logger.warning("{} not found!".format(fund_code))
    
def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text

def get_fund_nav(fund_code, end_date=None, start_date=None, duration=90):
    invalid_flag = False
    last_day = dt.date.today()
    try:
        end_dt = str2date(end_date)
    except (ValueError, TypeError):
        invalid_flag = True
        end_dt = last_day
        end_date = str(end_dt)
    try:
        start_dt = str2date(start_date)
    except (ValueError, TypeError):
        invalid_flag = True
        # start_dt = end_dt - dt.timedelta(days=duration)
        start_dt = get_another_day(end_dt, duration)
        start_date = str(start_dt)
    if invalid_flag:
        my_logger.warning("Invalid date, use ({}, {}) instead.".format(start_date, end_date))

    ## Get DataFrame if it has been saved already
    data_filename = "./data/Fund_{}_{}_{}.csv".format(fund_code, start_date, end_date)
    if os.path.isfile(data_filename):
        return pd.read_csv(data_filename)

    ## Get data with eastmoney API
    days = (end_dt - start_dt).days

    url = "http://fund.eastmoney.com/f10/F10DataApi.aspx"
    params = {  "type":     "lsjz", 
                "code":     fund_code, 
                "sdate":    start_date, 
                "edate":    end_date,
                "per":      days,
                "page":     1,
    }
    html = get_url(url, params)
    ## return val should be "pages:xxx"
    num_pages = int(re.search("pages:[0-9]+", html).group()[6:])
    my_logger.info("Total page of NAV is {}".format(num_pages))
    
    def convert2df(soup):
        ## Get table headers
        table_heads = list()
        for head in soup.findAll("th"):
            table_heads.append(head.contents[0])
        ## Get table rows (data)
        table_rows = list()
        for rows in soup.findAll("tbody")[0].findAll("tr"):
            table_records = list()
            for record in rows.findAll("td"):
                val = record.contents
                ## Replace empty element with nan
                if len(val) == 0:
                    table_records.append(np.nan)
                else:
                    table_records.append(val[0])
            table_rows.append(table_records)
        ## Convert to DataFrame
        table_rows = np.array(table_rows)
        df = pd.DataFrame()
        for col, col_name in enumerate(table_heads):
            if col_name in ["申购状态", "赎回状态"]:
                continue
            df[header_dict[col_name]] = table_rows[:,col]
        ## Add weekday column
        df["Weekday"] = df.get("Date").apply(lambda _str: str2date(_str).isoweekday())
        return df
    
    soup = BeautifulSoup(html, "html.parser")
    df = convert2df(soup)
    for page_idx in range(1, num_pages):
        params["page"] = page_idx + 1
        my_logger.info("Processing fund {} page {}".format(fund_code, params["page"]))
        html = get_url(url, params)
        soup = BeautifulSoup(html, "html.parser")
        df = df.append(convert2df(soup))
    df = df.reset_index()
    df.pop("index")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get NAV of funds")
    parser.add_argument("--fund_code", type=str, default="000051",
                        help="the fund code")
    parser.add_argument("--start_date", type=str, default=None,
                        help="the start date")
    parser.add_argument("--end_date", type=str, default=None,
                        help="the end date")
    parser.add_argument("--save", type=bool, default=False,
                        help="whether to save dataframe")
    args = parser.parse_args()

    ## Create Pandas dataframe
    df = get_fund_nav(args.fund_code, args.start_date, args.end_date)
    my_logger.info("Fund code: {}, name: {}\n{}".format(args.fund_code, get_fund_info(args.fund_code, 2), df.head(10)))

    if args.save:
        start_date = str(df.loc[df.index[0]]["Date"])
        end_date = str(df.loc[df.index[-1]]["Date"])
        df.to_csv("./data/Fund_{}_{}_{}.csv".format(args.fund_code, start_date, end_date))
