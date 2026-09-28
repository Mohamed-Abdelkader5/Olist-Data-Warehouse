import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BASE_DIR))

from logs.logger import get_logger
from config.config_loader import load_config


logger = get_logger()


def extract_csv(file_name):

    file_path = BASE_DIR / "data_sets" / file_name

    logger.info(f"Starting extraction: {file_name}")

    if not file_path.exists():

        logger.error(f"File not found: {file_path}")

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    logger.info(
        f"Extraction completed: {file_name} | "
        f"Rows: {len(df)} | "
        f"Columns: {len(df.columns)}"
    )

    return df


def extract_all_data():

    config = load_config()

    files = config["data"]["files"]

    data = {}

    for table_name, file_name in files.items():

        logger.info(f"Processing table: {table_name}")

        data[table_name] = extract_csv(file_name)

    logger.info("All tables extracted successfully")

    return data


if __name__ == "__main__":

    data = extract_all_data()

    print(data.keys())