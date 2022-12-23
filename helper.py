import os
import sys
from pathlib import Path

import yaml
from sqlalchemy import create_engine, inspect

from logger import logger


def config_file():
    if os.path.exists("config/config.yaml") == False:
        Path("config/config.yaml").touch()
        logger.info("Config file created")
        config_dict = {
            "connection_string": "mysql+pymysql://username:password@ip:3306/db?charset=utf8mb4",
            "wan_adr": "",
            "transaction_table": "",
            "koinly_table": "",
            "pages": "",
        }
        with open("config/config.yaml", "w") as ymlfile:
            yaml.dump(config_dict, ymlfile, default_flow_style=False)
    else:
        logger.info("Config file already exists")


def load_config():
    config_file()
    # Loading Yaml file
    with open("config/config.yaml", "r") as ymlfile:
        try:
            cfg = yaml.safe_load(ymlfile)
            logger.info("Yaml file correcly loaded")
        except yaml.YAMLError as exc:
            logger.error("Error in config file:", exc)
    return cfg


def applying_config(cfg):
    # Checking if all configs are present
    try:
        connection_string = cfg["connection_string"]
        transaction_table = cfg["transaction_table"]
        koinly_table = cfg["koinly_table"]
        wan_adr = cfg["wan_adr"]
        pages_chosen = cfg["pages"]
        logger.info("All settings loaded correctly")
    except KeyError as exc:
        logger.error("Error loading config", exc)
    return connection_string, transaction_table, koinly_table, wan_adr, pages_chosen


def transactions_check():
    try:
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        if inspector.has_table(transaction_table) == True:
            return False
        else:
            return True
    except Exception as exc:
        logger.error(
            "Error connecting to database - Please check configuration", exc_info=True
        )

        sys.exit()


(
    connection_string,
    transaction_table,
    koinly_table,
    wan_adr,
    pages_chosen,
) = applying_config(cfg=load_config())

ALL_TRANSACTIONS = transactions_check()
