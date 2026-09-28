import sys
from pathlib import Path

import pandas as pd


# ============================================================
# Project Path
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(BASE_DIR))


# ============================================================
# Imports
# ============================================================
from etl.load import load_all_data
from logs.logger import get_logger

from etl.extract import extract_all_data

from etl.transform import (
    transform_customers,
    transform_geolocation,
    transform_order,
    transform_order_items,
    transform_order_payments,
    transform_reviews,
    transform_products,
    transform_sellers,
    transform_category_translation,
    save_processed_data
)


# ============================================================
# Pandas Display Options
# ============================================================

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)
pd.set_option("display.expand_frame_repr", True)


# ============================================================
# Logger
# ============================================================

logger = get_logger()


# ============================================================
# Show Basic Information
# ============================================================

def show_basic_info(df):

    print("\n--- First 5 Rows ---")
    print(df.head())

    print("\n--- Shape ---")
    print(df.shape)

    print("\n--- Columns ---")
    print(df.columns.tolist())

    print("\n--- Data Types ---")
    print(df.dtypes)

    print("\n--- Null Values ---")
    print(df.isnull().sum())

    print("\n--- Duplicated Rows ---")
    print(df.duplicated().sum())


# ============================================================
# Run Transformation
# ============================================================

def run_transformation(data, table_name, transform_function):

    df = data[table_name]

    logger.info(
        f"Processing table: {table_name}"
    )

    print("\n" + "=" * 60)
    print(f"TABLE: {table_name}")
    print("=" * 60)

    print(
        "\n---------------------- BEFORE TRANSFORMATION -----------------"
    )

    show_basic_info(df)

    # Transformation
    df = transform_function(df)

    print(
        "\n------------------------ AFTER TRANSFORMATION -----------------"
    )

    show_basic_info(df)

    logger.info(
        f"Transformation completed: {table_name}"
    )

    return df


# ============================================================
# Main Pipeline
# ============================================================

def main():

    logger.info("ETL Pipeline Started")

    print("\n" + "=" * 60)
    print("             DW PROJECT - ETL PIPELINE")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Extract
    # --------------------------------------------------------

    logger.info("Starting extraction of all tables")

    data = extract_all_data()

    logger.info("All tables extracted successfully")

    # --------------------------------------------------------
    # 2. Transformation Mapping
    # --------------------------------------------------------

    transformations = {

        "customers": transform_customers,

        "geolocation": transform_geolocation,

        "orders": transform_order,

        "order_items": transform_order_items,

        "payments": transform_order_payments,

        "reviews": transform_reviews,

        "products": transform_products,

        "sellers": transform_sellers,

        "category_translation": transform_category_translation

    }

    # --------------------------------------------------------
    # 3. Transform All Tables
    # --------------------------------------------------------

    transformed_data = {}

    for table_name, transform_function in transformations.items():

        try:

            result = run_transformation(
                data,
                table_name,
                transform_function
            )

            transformed_data[table_name] = result

        except Exception as e:

            logger.error(
                f"Transformation failed for {table_name}: {e}"
            )

            print(
                f"\nERROR while transforming {table_name}: {e}"
            )

    # --------------------------------------------------------
    # 4. Save Processed Data
    # --------------------------------------------------------

    logger.info("Starting saving processed data")

    save_processed_data(transformed_data)

    logger.info("Processed data saved successfully")
    logger.info("Starting database load")

    load_all_data()

    logger.info("Database load completed successfully")

    # --------------------------------------------------------
    # 5. Pipeline Finished
    # --------------------------------------------------------

    logger.info("Transformation phase completed")

    print("\n" + "=" * 60)
    print("       TRANSFORMATION PHASE COMPLETED")
    print("=" * 60)

    print("\nTransformed Tables:")

    for table_name in transformed_data:

        print(f"✓ {table_name}")

    logger.info("ETL Pipeline Finished")


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()