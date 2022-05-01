import os
from pathlib import touch

import yaml
from sqlalchemy import create_engine, inspect

if os.path.exists("config/config.yml") == False:
    touch("config/config.yaml")
    print("Config file created")
    config_dict = {
        "connection_string": "mysql+pymysql://username:password@ip:3306/db?charset=utf8mb4",
        "wan_adr": "",
        "transaction_table": "",
        "koinly_table": "",
    }
    with open("config/config.yaml", "w") as ymlfile:
        yaml.dump(config_dict, ymlfile, default_flow_style=False)
else:
    print("Config file already exists")


def load_config():
    # Loading Yaml file
    with open("config/config.yaml", "r") as ymlfile:
        try:
            cfg = yaml.safe_load(ymlfile)
            print("Yaml file correcly loaded")
        except yaml.YAMLError as exc:
            print("Error in config file:", exc)
    return cfg


def applying_config(cfg):
    # Checking if all configs are present
    try:
        connection_string = cfg["connection_string"]
        transaction_table = cfg["transaction_table"]
        koinly_table = cfg["koinly_table"]
        wan_adr = cfg["wan_adr"]
        print("All settings loaded correctly")
    except KeyError as exc:
        print("Error loading config", exc)
    return connection_string, transaction_table, koinly_table, wan_adr


def transactions_check():
    engine = create_engine(connection_string)
    inspector = inspect(engine)
    if inspector.has_table(transaction_table) == True:
        return False
    else:
        return True


connection_string, transaction_table, koinly_table, wan_adr = applying_config(
    cfg=load_config()
)

ALL_TRANSACTIONS = transactions_check()
