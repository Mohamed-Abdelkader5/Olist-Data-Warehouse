
import os
import pyodbc

from logs.logger import get_logger


# ============================================================
# LOGGER
# ============================================================

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
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = pyodbc.connect(
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    return connection


# ============================================================
# CLEAR DATA WAREHOUSE
# ============================================================

def clear_datawarehouse(cursor):

    logger.info("Clearing Data Warehouse tables")

    # --------------------------------------------------------
    # STEP 1: DELETE FACT TABLE FIRST
    # --------------------------------------------------------

    cursor.execute("""
        DELETE FROM dbo.Fact_Sales
    """)

    logger.info("✓ Fact_Sales cleared")

    # --------------------------------------------------------
    # STEP 2: DELETE DIMENSIONS
    # --------------------------------------------------------

    cursor.execute("""
        DELETE FROM dbo.DimDate
    """)

    cursor.execute("""
        DELETE FROM dbo.DimReview
    """)

    cursor.execute("""
        DELETE FROM dbo.DimPayment
    """)

    cursor.execute("""
        DELETE FROM dbo.DimSeller
    """)

    cursor.execute("""
        DELETE FROM dbo.DimProduct
    """)

    cursor.execute("""
        DELETE FROM dbo.DimCustomer
    """)

    logger.info("✓ Data Warehouse tables cleared")


# ============================================================
# LOAD DIM CUSTOMER
# ============================================================

def load_dim_customer(cursor):

    logger.info("Loading DimCustomer")

    cursor.execute("""
        INSERT INTO dbo.DimCustomer
        (
            Customer_ID,
            Customer_Unique_ID,
            Customer_Zip_Code,
            Customer_City,
            Customer_State
        )
        SELECT
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        FROM staging.stg_customers;
    """)

    logger.info("✓ DimCustomer loaded")


# ============================================================
# LOAD DIM PRODUCT
# ============================================================

def load_dim_product(cursor):

    logger.info("Loading DimProduct")

    cursor.execute("""
        INSERT INTO dbo.DimProduct
        (
            product_id,
            Product_Category_Name,
            Product_Name_Length,
            Product_Description_Length,
            Product_Photos_Qty,
            Product_Weight_G,
            Product_Length_CM,
            Product_Height_CM,
            Product_Width_CM
        )
        SELECT
            product_id,
            product_category_name,
            product_name_lenght,
            product_description_lenght,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm
        FROM staging.stg_products;
    """)

    logger.info("✓ DimProduct loaded")


# ============================================================
# LOAD DIM SELLER
# ============================================================

def load_dim_seller(cursor):

    logger.info("Loading DimSeller")

    cursor.execute("""
        INSERT INTO dbo.DimSeller
        (
            Seller_ID,
            Seller_Zip_Code,
            Seller_City,
            Seller_State
        )
        SELECT
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        FROM staging.stg_sellers;
    """)

    logger.info("✓ DimSeller loaded")


# ============================================================
# LOAD DIM PAYMENT
# ============================================================

def load_dim_payment(cursor):

    logger.info("Loading DimPayment")

    cursor.execute("""
        INSERT INTO dbo.DimPayment
        (
            Payment_Type,
            Payment_Installments
        )
        SELECT DISTINCT
            payment_type,
            payment_installments
        FROM staging.stg_payments;
    """)

    logger.info("✓ DimPayment loaded")


# ============================================================
# LOAD DIM REVIEW
# ============================================================

def load_dim_review(cursor):

    logger.info("Loading DimReview")

    cursor.execute("""
        INSERT INTO dbo.DimReview
        (
            Review_Score,
            Review_Title
        )
        SELECT DISTINCT
            review_score,
            review_comment_title
        FROM staging.stg_reviews;
    """)

    logger.info("✓ DimReview loaded")


# ============================================================
# LOAD DIM DATE
# ============================================================

def load_dim_date(cursor):

    logger.info("Loading DimDate")

    cursor.execute("""
        INSERT INTO dbo.DimDate
        (
            DateKey,
            FullDate,
            DayNumber,
            DayName,
            WeekNumber,
            MonthNumber,
            MonthName,
            QuarterNumber,
            YearNumber
        )
        SELECT DISTINCT
            CONVERT(INT, FORMAT(OrderDate, 'yyyyMMdd')) AS DateKey,
            OrderDate AS FullDate,
            DAY(OrderDate) AS DayNumber,
            DATENAME(WEEKDAY, OrderDate) AS DayName,
            DATEPART(WEEK, OrderDate) AS WeekNumber,
            MONTH(OrderDate) AS MonthNumber,
            DATENAME(MONTH, OrderDate) AS MonthName,
            DATEPART(QUARTER, OrderDate) AS QuarterNumber,
            YEAR(OrderDate) AS YearNumber
        FROM
        (
            SELECT CAST(order_purchase_timestamp AS DATE) AS OrderDate
            FROM staging.stg_orders
            WHERE order_purchase_timestamp IS NOT NULL

            UNION

            SELECT CAST(order_approved_at AS DATE)
            FROM staging.stg_orders
            WHERE order_approved_at IS NOT NULL

            UNION

            SELECT CAST(order_delivered_carrier_date AS DATE)
            FROM staging.stg_orders
            WHERE order_delivered_carrier_date IS NOT NULL

            UNION

            SELECT CAST(order_delivered_customer_date AS DATE)
            FROM staging.stg_orders
            WHERE order_delivered_customer_date IS NOT NULL

            UNION

            SELECT CAST(order_estimated_delivery_date AS DATE)
            FROM staging.stg_orders
            WHERE order_estimated_delivery_date IS NOT NULL

        ) AS Dates;
    """)

    logger.info("✓ DimDate loaded")


# ============================================================
# LOAD FACT SALES
# ============================================================
def load_fact_sales(cursor):

    logger.info("Loading Fact_Sales")

    cursor.execute("""
        INSERT INTO dbo.Fact_Sales
        (
            Order_Id,
            Order_Item_Id,
            Customer_Key,
            Product_Key,
            Seller_Key,
            Order_Date_Key,
            Price,
            Freight_Value
        )
        SELECT
            o.order_id,
            oi.order_item_id,

            dc.Customer_Key,
            dp.product_key,
            ds.Seller_Key,

            CONVERT(
                INT,
                FORMAT(
                    CAST(o.order_purchase_timestamp AS DATE),
                    'yyyyMMdd'
                )
            ) AS Order_Date_Key,

            oi.price,
            oi.freight_value

        FROM staging.stg_orders o

        INNER JOIN staging.stg_order_items oi
            ON o.order_id = oi.order_id

        INNER JOIN dbo.DimCustomer dc
            ON o.customer_id = dc.Customer_ID

        INNER JOIN dbo.DimProduct dp
            ON oi.product_id = dp.product_Id

        INNER JOIN dbo.DimSeller ds
            ON oi.seller_id = ds.Seller_ID

        WHERE o.order_purchase_timestamp IS NOT NULL;
    """)

    logger.info("✓ Fact_Sales loaded")




# ============================================================
# LOAD DATA WAREHOUSE
# ============================================================

def load_datawarehouse():

    logger.info("Starting Data Warehouse load")

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # CLEAR OLD DATA
        # ----------------------------------------------------

        clear_datawarehouse(cursor)

        # ----------------------------------------------------
        # COMMIT CLEAR
        # ----------------------------------------------------

        connection.commit()

        logger.info("✓ Old Data Warehouse data committed")

        # ----------------------------------------------------
        # LOAD DIMENSIONS
        # ----------------------------------------------------

        load_dim_customer(cursor)

        load_dim_product(cursor)

        load_dim_seller(cursor)

        load_dim_payment(cursor)

        load_dim_review(cursor)

        load_dim_date(cursor)

        # ----------------------------------------------------
        # LOAD FACT
        # ----------------------------------------------------

        load_fact_sales(cursor)

        # ----------------------------------------------------
        # COMMIT NEW DATA
        # ----------------------------------------------------

        connection.commit()

        logger.info("Data Warehouse loaded successfully")

        print("\nALL DATA WAREHOUSE TABLES LOADED SUCCESSFULLY")

    except Exception as e:

        connection.rollback()

        logger.error(f"Data Warehouse load failed: {e}")

        raise

    finally:

        cursor.close()
        connection.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    load_datawarehouse()

