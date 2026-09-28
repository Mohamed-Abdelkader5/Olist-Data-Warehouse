import sys
import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BASE_DIR))


# ============================================================
# IMPORT LOGGER
# ============================================================

from logs.logger import get_logger


logger = get_logger()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================
SERVER = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DRIVER = os.getenv("DB_DRIVER")


# ============================================================
# CONNECTION STRING
# ============================================================

ODBC_CONNECTION = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "TrustServerCertificate=yes;"
)

CONNECTION_STRING = (
    "mssql+pyodbc:///?odbc_connect="
    + quote_plus(ODBC_CONNECTION)
)


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    CONNECTION_STRING,
    fast_executemany=True
)


# ============================================================
# PROCESSED DATA PATH
# ============================================================

PROCESSED_DIR = (
    BASE_DIR
    / "data_sets"
    / "processed"
)


# ============================================================
# TABLE MAPPING
# ============================================================

TABLES = {

    "customers": "stg_customers",

    "geolocation": "stg_geolocation",

    "order_items": "stg_order_items",

    "payments": "stg_payments",

    "reviews": "stg_reviews",

    "orders": "stg_orders",

    "products": "stg_products",

    "sellers": "stg_sellers",

    "category_translation": "stg_category_translation"

}


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

def test_connection():

    logger.info("Testing database connection")

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT DB_NAME()")
            )

            database_name = result.scalar()

            logger.info(
                f"Database connection successful: "
                f"{database_name}"
            )

            print("\n✓ Connected to SQL Server")

            print(
                f"✓ Database: {database_name}"
            )

    except Exception as e:

        logger.error(
            f"Database connection failed: {e}"
        )

        print(
            "\n✗ Database connection failed"
        )

        print(e)

        raise


# ============================================================
# CREATE STAGING SCHEMA
# ============================================================

def create_staging_schema():

    logger.info("Checking staging schema")

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM sys.schemas
                    WHERE name = 'staging'
                )
                BEGIN
                    EXEC('CREATE SCHEMA staging')
                END
                """
            )
        )

    logger.info(
        "Staging schema is ready"
    )


# ============================================================
# LOAD ONE TABLE
# ============================================================

def load_table(
    table_name,
    staging_table_name
):

    file_path = (
        PROCESSED_DIR
        / f"{table_name}.csv"
    )

    logger.info(
        f"Starting load: {table_name}"
    )

    print("\n" + "=" * 60)

    print(
        f"LOADING: {table_name}"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file_path.exists():

        logger.error(
            f"Processed file not found: "
            f"{file_path}"
        )

        raise FileNotFoundError(
            f"Processed file not found: "
            f"{file_path}"
        )


    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    df = pd.read_csv(
        file_path
    )

    logger.info(
        f"CSV loaded: {table_name} | "
        f"Rows: {len(df)} | "
        f"Columns: {len(df.columns)}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )


    # --------------------------------------------------------
    # LOAD INTO SQL SERVER
    # --------------------------------------------------------

    df.to_sql(

        name=staging_table_name,

        con=engine,

        schema="staging",

        if_exists="replace",

        index=False

    )


    logger.info(
        f"Loaded successfully: "
        f"staging.{staging_table_name}"
    )

    print(
        f"✓ Loaded into "
        f"staging.{staging_table_name}"
    )


# ============================================================
# LOAD ALL TABLES
# ============================================================

def load_all_data():

    logger.info(
        "Starting database load"
    )

    print("\n" + "=" * 60)

    print(
        "             DW PROJECT - LOAD"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # 1. TEST DATABASE CONNECTION
    # --------------------------------------------------------

    test_connection()


    # --------------------------------------------------------
    # 2. CREATE STAGING SCHEMA
    # --------------------------------------------------------

    create_staging_schema()


    # --------------------------------------------------------
    # 3. LOAD ALL TABLES
    # --------------------------------------------------------

    for table_name, staging_table_name in TABLES.items():

        try:

            load_table(
                table_name,
                staging_table_name
            )

        except Exception as e:

            logger.error(
                f"Load failed for "
                f"{table_name}: {e}"
            )

            print(
                f"\n✗ ERROR loading "
                f"{table_name}"
            )

            print(e)

            raise


    # --------------------------------------------------------
    # 4. FINISHED
    # --------------------------------------------------------

    logger.info(
        "All staging tables loaded successfully"
    )

    print("\n" + "=" * 60)

    print(
        "       ALL DATA LOADED SUCCESSFULLY"
    )

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    load_all_data()