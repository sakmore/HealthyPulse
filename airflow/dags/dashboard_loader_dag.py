from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests

def ping_streamlit():
    try:
        response = requests.get("http://host.docker.internal:8501/refresh")  # If you have an endpoint
        print("Dashboard refresh triggered:", response.text)
    except Exception as e:
        print("Dashboard refresh failed:", e)

with DAG(
    dag_id="dashboard_loader_every_5_min",
    start_date=datetime(2025, 7, 21),
    schedule_interval="*/5 * * * *",  # Every 5 minutes
    catchup=False
) as dag:

    refresh_dash = PythonOperator(
        task_id="trigger_streamlit_refresh",
        python_callable=ping_streamlit
    )
