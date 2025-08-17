from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from kafka import KafkaConsumer
import json
import psycopg2

def consume_and_store():
    try:
        consumer = KafkaConsumer(
            'patient_vitals',
            bootstrap_servers=['host.docker.internal:9092'],
            auto_offset_reset='earliest',
            group_id='health-consumer-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=10000  # 10 second timeout
        )

        conn = psycopg2.connect(
            dbname='healthdb',
            user='postgres',
            password='postgres',  # Update with your actual password
            host='host.docker.internal',
            port='5432'
        )
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vitals (
                id SERIAL PRIMARY KEY,
                hadm_id VARCHAR(255),
                heart_rate INTEGER,
                temperature FLOAT,
                oxygen_level INTEGER,
                mask_type INTEGER,
                timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        message_count = 0
        for message in consumer:
            data = message.value
            print(f"Received message: {data}")

            # Map your actual data fields
            try:
                cursor.execute(
                    """
                    INSERT INTO vitals (hadm_id, heart_rate, temperature, oxygen_level, mask_type, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (data['hadm_id'], data['HR'], data['TEMP'], data['SPO2'], data['masktype'], data['timestamp'])
                )
                conn.commit()
                print(f"Inserted: {data}")
                message_count += 1
                
                # Process only a few messages per run to avoid long-running tasks
                if message_count >= 5:
                    break
                    
            except KeyError as e:
                print(f"Missing key in message: {e}, Data: {data}")
            except Exception as e:
                print(f"Error inserting data: {e}")

        consumer.close()
        cursor.close()
        conn.close()
        
        print(f"Processed {message_count} messages")
        
    except Exception as e:
        print(f"Error in consume_and_store: {e}")
        raise

with DAG(
    dag_id="kafka_consumer_to_postgres",
    start_date=datetime(2025, 7, 21),
    schedule_interval="*/5 * * * *",  # Every 5 minutes
    catchup=False,
    max_active_runs=1  # Prevent overlapping runs
) as dag:

    consume_task = PythonOperator(
        task_id="consume_kafka_store_postgres",
        python_callable=consume_and_store
    )