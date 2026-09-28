USE DW;
GO

SELECT * FROM staging.stg_orders
select * from staging.stg_order_items
select * from staging.stg_products
select * from staging.stg_payments

------------------------------------------------------
USE dw;
GO
create table Customer(
    Customer_Key   INT IDENTITY(1,1)  primary key ,
    Customer_Id     varchar(60)      Not null ,
    Customer_Unique_ID VARCHAR(50),
    Customer_Zip_Code INT,
    Customer_City VARCHAR(100),
    Customer_State VARCHAR(10)
);
GO
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

select count(*) from Dimcustomer
----------------------------------------------------------------------------------------
USE DW;
GO
create table DimProduct( 
    product_key  int identity (1,1) primary key ,
    product_Id   varchar(50) not null,
	Product_Category_Name VARCHAR(100),
    Product_Name_Length INT,
    Product_Description_Length INT,
    Product_Photos_Qty INT,
    Product_Weight_G INT,
    Product_Length_CM DECIMAL(10,2),
    Product_Height_CM DECIMAL(10,2),
    Product_Width_CM DECIMAL(10,2)
);
GO

 insert into DimProduct(
  
    product_id   ,
	Product_Category_Name ,
    Product_Name_Length ,
    Product_Description_Length ,
    Product_Photos_Qty ,
    Product_Weight_G,
    Product_Length_CM ,
    Product_Height_CM
 )
 select  
 product_id,
 product_category_name,
 product_name_lenght,
 product_description_lenght,
 product_photos_qty,
 product_weight_g,
product_length_cm,
product_height_cm
 
 from staging.stg_products;
 select * from DimProduct
 
SELECT COUNT(*) AS row_count
FROM dbo.DimProduct;
GO
 --------------------------------------------------------------------------------------
 -------------------------------------------------------------------------------------

CREATE TABLE dbo.DimSeller
(
    Seller_Key INT IDENTITY(1,1) PRIMARY KEY,

    Seller_ID VARCHAR(60) NOT NULL,

    Seller_Zip_Code INT,

    Seller_City VARCHAR(100),

    Seller_State VARCHAR(10)
);
GO


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
GO

SELECT COUNT(*) AS row_count
FROM dbo.DimSeller;
GO
-------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------
CREATE TABLE dbo.DimPayment
(
    Payment_Key INT IDENTITY(1,1) PRIMARY KEY,

    Payment_Type VARCHAR(50),

    Payment_Installments INT
);
GO


INSERT INTO dbo.DimPayment
(
    Payment_Type,
    Payment_Installments
)
SELECT DISTINCT
    payment_type,
    payment_installments
FROM staging.stg_payments;
GO


SELECT *
FROM dbo.DimPayment;
GO
------------------------------------------------------------------------------
----------------------------------------------------------------------------------


CREATE TABLE dbo.DimReview
(
    Review_Key INT IDENTITY(1,1) PRIMARY KEY,

    Review_Score INT,

    Review_Title VARCHAR(300)
);
GO


INSERT INTO dbo.DimReview
(
    Review_Score,
    Review_Title
)
SELECT DISTINCT
    review_score,
    review_comment_title
FROM staging.stg_reviews;
GO

SELECT COUNT(*) AS row_count
FROM dbo.DimReview;
GO
---------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------
  
  USE DW;
GO

CREATE TABLE dbo.DimDate
(
    DateKey INT PRIMARY KEY,
    FullDate DATE NOT NULL,
    DayNumber INT,
    DayName VARCHAR(20),
    WeekNumber INT,
    MonthNumber INT,
    MonthName VARCHAR(20),
    QuarterNumber INT,
    YearNumber INT
);
GO
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
GO

select * from DimDate
--*************************************************************************
--*********************************************************************************************


SELECT * from DimCustomer