import pandas as pd
import requests
from lxml import html
from pangres import upsert
from sqlalchemy import create_engine, inspect

from helper import (
    ALL_TRANSACTIONS,
    connection_string,
    headers,
    koinly_table,
    pages_chosen,
    transaction_table,
    wan_adr,
)
from logger import logger


class Data_Ret:
    def __init__(self):
        self.adr = wan_adr
        self.data = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def get_total_pages(self):
        if ALL_TRANSACTIONS == False:
            return pages_chosen
        else:
            page = requests.get(
                f"https://www.wanscan.org/rewardD?addr={self.adr}&page=1&validator=undefined",
                headers=self.headers,
            )
            tree = html.fromstring(page.content)
            pages = tree.xpath("/html/body/div/div[2]/div[2]/h4/span/text()")
            pages = int(pages[0].split(" ")[-1])
            return pages

    def get_data(self):
        page = 0
        for page in range(0, self.get_total_pages()):
            page += 1
            response = requests.get(
                f"https://www.wanscan.org/rewardD?addr={self.adr}&page={page}&validator=undefined",
                headers=self.headers,
            )
            df = pd.read_html(response.content)[0]
            self.data.append(df)
            logger.info(f"Done with page : {page}")
        return self.data

    def cleaning_data(self):
        raw_data = pd.concat(self.get_data())
        raw_data = raw_data.drop(columns=["No"])
        raw_data["Currency"] = "WAN"
        raw_data["Amount"] = raw_data.Reward.str.strip("WAN")
        raw_data.Amount = raw_data.Amount.astype(float)
        raw_data.drop("Unnamed: 4", axis="columns", inplace=True)
        raw_data.drop("Reward", axis="columns", inplace=True)

        return raw_data

    def get_block_dates(self):
        _data = self.cleaning_data()
        logger.info("Getting dates from blocks")
        _data["Date"] = _data["Block"].apply(
            lambda x: pd.read_html(
                requests.get(
                    f"https://www.wanscan.org/block/{x}",
                    headers=self.headers,
                ).content
            )[0].T.iloc[1:, 2]
        )
        _data["Date"] = _data["Date"].apply(lambda x: x.split("(")[1].split(")")[0])
        _data["Date"] = _data.Date.apply(lambda x: x.replace("Spt", "Sep"))
        _data["Date"] = pd.to_datetime(_data["Date"], format="%b-%d-%Y %H:%M:%S +%Z")
        return _data

    def transactional_data(self):
        _data = self.get_block_dates()
        _data.set_index("Epoch", inplace=True)
        _data.drop("Validator", axis="columns", inplace=True)
        return _data


def koinly_format(data):
    _data_koinly = data.copy()
    _data_koinly = _data_koinly.loc[:, ["Date", "Amount", "Currency"]]
    _data_koinly["label"] = "Reward"
    _data_koinly = _data_koinly.set_index("Date")
    _data_koinly.index.name = "Koinly Date"
    return _data_koinly


class export_to_sql:
    def __init__(
        self,
        wan_tran=transaction_table,
        koinly_tran=koinly_table,
        con_str=connection_string,
    ):
        self.engine = create_engine(con_str)
        self.wan_tran = wan_tran
        self.koinly_tran = koinly_tran

    def trans_sql(self, data):
        upsert(
            con=self.engine, df=data, table_name=self.wan_tran, if_row_exists="ignore"
        )

    def koinly_sql(self, data):
        upsert(
            con=self.engine,
            df=data,
            table_name=self.koinly_tran,
            if_row_exists="ignore",
        )

    def has_table(self, table_name):
        inspector = inspect(self.engine)
        return inspector.has_table(table_name)


# Get staking data from wanchain
logger.info("Getting data from wanchain.....")
trans_df = Data_Ret().transactional_data()

# Exporting data to SQL table as specified in the configuration file
logger.info("Exporting data to SQL.....")
export_to_sql().trans_sql(trans_df)
export_to_sql().koinly_sql(koinly_format(trans_df))
logger.info("Sucesfully exported Wanchain data to SQL server")
