import pandas as pd
import sys
from pathlib import Path


# ==========================================================
# Project Path
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(BASE_DIR))


# ==========================================================
# Imports
# ==========================================================

from etl.extract import extract_all_data
from logs.logger import get_logger


# ==========================================================
# Logger
# ==========================================================

logger = get_logger()


# ==========================================================
# Processed Data Path
# ==========================================================

PROCESSED_PATH = BASE_DIR / "data_sets" / "processed"

PROCESSED_PATH.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# Clean Column Names
# ==========================================================

def clean_column_name(df):

    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


# ==========================================================
# Customers
# ==========================================================

def transform_customers(df):

    logger.info("Starting transformation: customers")

    df = df.copy()

    df = df.drop_duplicates()

    df["customer_city"] = (
        df["customer_city"]
        .str.strip()
        .str.lower()
    )

    df["customer_state"] = (
        df["customer_state"]
        .str.strip()
        .str.upper()
    )

    return df


# ==========================================================
# Geolocation
# ==========================================================

def transform_geolocation(df: pd.DataFrame):

    logger.info("Starting transformation: geolocation")

    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean city
    df["geolocation_city"] = (
        df["geolocation_city"]
        .str.strip()
        .str.lower()
    )

    # Clean state
    df["geolocation_state"] = (
        df["geolocation_state"]
        .str.strip()
        .str.upper()
    )

    # Convert zip code to numeric
    df["geolocation_zip_code_prefix"] = pd.to_numeric(
        df["geolocation_zip_code_prefix"],
        errors="coerce"
    )

    return df


# ==========================================================
# Orders
# ==========================================================

def transform_order(df: pd.DataFrame):

    logger.info("Starting transformation: orders")

    df = df.copy()

    # Convert date columns to datetime
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Remove rows with missing important data
    df = df.dropna()

    # Create delivery days
    df["delivery_days"] = (
        df["order_delivered_customer_date"]
        - df["order_purchase_timestamp"]
    ).dt.days

    # Create year
    df["year"] = (
        df["order_purchase_timestamp"]
        .dt.year
    )

    # Create month
    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.month
    )

    # Calculate late days
    df["late_days"] = (
        df["order_delivered_customer_date"]
        - df["order_estimated_delivery_date"]
    ).dt.days.clip(lower=0)

    return df


# ==========================================================
# Order Items
# ==========================================================

def transform_order_items(df: pd.DataFrame):

    logger.info("Starting transformation: order_items")

    df = df.copy()

    # Convert shipping date
    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    # Create total price
    df["total_price"] = (
        df["price"]
        + df["freight_value"]
    )

    return df


# ==========================================================
# Order Payments
# ==========================================================

def transform_order_payments(df: pd.DataFrame):

    logger.info("Starting transformation: payments")

    df = df.copy()

    # Clean payment type
    df["payment_type"] = (
        df["payment_type"]
        .str.strip()
        .str.lower()
    )

    return df


# ==========================================================
# Order Reviews
# ==========================================================

def transform_reviews(df):

    logger.info("Starting transformation: reviews")

    df = df.copy()

    # Remove duplicated reviews
    df = df.drop_duplicates()

    # Convert date columns to datetime
    df["review_creation_date"] = pd.to_datetime(
        df["review_creation_date"],
        errors="coerce"
    )

    df["review_answer_timestamp"] = pd.to_datetime(
        df["review_answer_timestamp"],
        errors="coerce"
    )

    # Clean review title
    df["review_comment_title"] = (
        df["review_comment_title"]
        .fillna("no comment")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Clean review message
    df["review_comment_message"] = (
        df["review_comment_message"]
        .fillna("no comment")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Remove rows only when important fields are missing
    df = df.dropna(
        subset=[
            "review_id",
            "order_id",
            "review_score",
            "review_creation_date",
            "review_answer_timestamp"
        ]
    )

    logger.info(
        f"Transformation completed: reviews | Rows: {len(df)}"
    )

    return df


# ==========================================================
# Products
# ==========================================================

def transform_products(df: pd.DataFrame):

    logger.info("Starting transformation: products")

    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean category
    df["product_category_name"] = (
        df["product_category_name"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Numeric columns
    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Fill missing numeric values
    df[numeric_columns] = df[numeric_columns].fillna(0)

    return df


# ==========================================================
# Sellers
# ==========================================================

def transform_sellers(df: pd.DataFrame):

    logger.info("Starting transformation: sellers")

    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean city
    df["seller_city"] = (
        df["seller_city"]
        .str.strip()
        .str.lower()
    )

    # Clean state
    df["seller_state"] = (
        df["seller_state"]
        .str.strip()
        .str.upper()
    )

    return df


# ==========================================================
# Product Category Translation
# ==========================================================

def transform_category_translation(df):

    logger.info("Starting transformation: category_translation")

    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean Portuguese category
    df["product_category_name"] = (
        df["product_category_name"]
        .str.strip()
        .str.lower()
    )

    # Clean English category
    df["product_category_name_english"] = (
        df["product_category_name_english"]
        .str.strip()
        .str.lower()
    )

    return df


# ==========================================================
# Transform All Data
# ==========================================================

def transform_all_data():

    logger.info("Starting transformation of all tables")

    # Extract all data
    data = extract_all_data()

    # Clean column names
    data = {
        table_name: clean_column_name(df)
        for table_name, df in data.items()
    }

    # Transform tables
    customers = transform_customers(
        data["customers"]
    )

    geolocation = transform_geolocation(
        data["geolocation"]
    )

    orders = transform_order(
        data["orders"]
    )

    order_items = transform_order_items(
        data["order_items"]
    )

    order_payments = transform_order_payments(
        data["payments"]
    )

    reviews = transform_reviews(
        data["reviews"]
    )

    products = transform_products(
        data["products"]
    )

    sellers = transform_sellers(
        data["sellers"]
    )

    category_translation = transform_category_translation(
        data["category_translation"]
    )

    # Collect transformed tables
    transformed_data = {

        "customers": customers,

        "geolocation": geolocation,

        "orders": orders,

        "order_items": order_items,

        "payments": order_payments,

        "reviews": reviews,

        "products": products,

        "sellers": sellers,

        "category_translation": category_translation
    }

    logger.info(
        "Transformation phase completed"
    )

    return transformed_data


# ==========================================================
# Save Processed Data
# ==========================================================

def save_processed_data(data):

    logger.info("Starting saving processed data")

    for table_name, df in data.items():

        file_path = (
            PROCESSED_PATH
            / f"{table_name}.csv"
        )

        df.to_csv(
            file_path,
            index=False
        )

        logger.info(
            f"Saved processed data: {file_path}"
        )


# ==========================================================
# Run Pipeline
# ==========================================================

if __name__ == "__main__":

    logger.info("ETL Transformation Started")

    transformed_data = transform_all_data()

    save_processed_data(
        transformed_data
    )

    logger.info(
        "All transformations completed successfully"
    )


