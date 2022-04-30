import yaml
from sqlalchemy import create_engine, inspect


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
