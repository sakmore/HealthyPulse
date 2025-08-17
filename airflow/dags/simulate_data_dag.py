from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import time

def hit_flask_multiple():
    # Try multiple host options for Docker to local communication
    base_urls = [
        "http://host.docker.internal:5000",  # Docker Desktop (Windows/Mac)
        "http://172.17.0.1:5000",           # Docker bridge network
        "http://gateway.docker.internal:5000"  # Alternative Docker gateway
    ]
    
    working_url = None
    
    for _ in range(12):  # 12 * 5 sec = 60 sec
        if not working_url:
            # Find working URL on first iteration
            for base_url in base_urls:
                try:
                    test_response = requests.get(f"{base_url}/send-vitals", timeout=3)
                    working_url = base_url
                    print(f"Found working URL: {working_url}")
                    break
                except Exception as e:
                    print(f"Failed to connect to {base_url}: {e}")
            
            if not working_url:
                print("Could not connect to Flask app with any URL")
                return
        
        try:
            response = requests.get(f"{working_url}/send-vitals")
            print("API response:", response.json())
        except Exception as e:
            print("Error calling Flask API:", e)
        time.sleep(5)

with DAG(
    dag_id="simulate_data_every_5_seconds",
    start_date=datetime(2025, 7, 21),
    schedule_interval="* * * * *",  # Every minute
    catchup=False
) as dag:

    simulate = PythonOperator(
        task_id="hit_flask_api_12_times",
        python_callable=hit_flask_multiple
    )