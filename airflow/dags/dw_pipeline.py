from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.extract import extract_all_data
from etl.transform import transform_all_data
from etl.load import load_all_data
from etl.datawarehouse import load_datawarehouse


# ============================================================
# DAG
# ============================================================

with DAG(
    dag_id="dw_pipeline",
    description="Olist Data Warehouse ETL Pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["DW", "ETL", "Olist"],
) as dag:

    # ========================================================
    # TASK: EXTRACT
    # ========================================================

    def extract_data():

        data = extract_all_data()

        print("\nExtracted tables:")

        for table_name, df in data.items():
            print(
                f"✓ {table_name}: "
                f"{len(df)} rows, "
                f"{len(df.columns)} columns"
            )

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
    )

    # ========================================================
    # TASK: TRANSFORM
    # ========================================================

    def transform_data():

        data = transform_all_data()

        print("\nTransformed tables:")

        for table_name, df in data.items():
            print(
                f"✓ {table_name}: "
                f"{len(df)} rows, "
                f"{len(df.columns)} columns"
            )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
    )

    # ========================================================
    # TASK: PROCESSED DATA
    # ========================================================

    def processed_data():

        data = transform_all_data()

        print("\nProcessed tables:")

        for table_name, df in data.items():
            print(
                f"✓ {table_name}: "
                f"{len(df)} rows, "
                f"{len(df.columns)} columns"
            )

    processed_task = PythonOperator(
        task_id="processed_data",
        python_callable=processed_data,
    )





# ========================================================
# TASK: LOAD
# ========================================================

    def load_data():

         load_all_data()

       


    load_task = PythonOperator(
        task_id="load_task",
        python_callable=load_data,
    )



# ========================================================
# TASK: DATA WAREHOUSE
# ========================================================

    def dw_load():

        load_datawarehouse()


    dw_load_task = PythonOperator(
        task_id="dw_load",
        python_callable=dw_load,
)





    # ========================================================
    # TASK DEPENDENCIES
    # ========================================================

    extract_task >> transform_task >> processed_task >> load_task >> dw_load_task
    

  


