from kafka import KafkaConsumer
import json
import psycopg2

from dotenv import load_dotenv
import os

load_dotenv() 

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")

try:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print(f"❌ Failed to connect to PostgreSQL: {e}")
    exit(1)

cursor = conn.cursor()

# Define anomaly detection function
def is_anomalous(vitals):
    return (
        vitals["HR"] < 50 or vitals["HR"] > 100 or
        vitals["TEMP"] < 95.0 or vitals["TEMP"] > 101.0 or
        vitals["SPO2"] < 94
    )

# Create Kafka consumer
consumer = KafkaConsumer(
    'patient_vitals',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='healthypulse_group'
)

print("Connected to Kafka and PostgreSQL successfully <3, Waiting for messages...")

for message in consumer:
    data = message.value
    print(f"YAYY Received message: {data} <3 <3 <3")

    # Check for anomaly
    if is_anomalous(data):
        print("⚠️⚠️ ALERT! Anomalous vitals detected ⚠️⚠️")
        print(f"🚨 Anomaly details: {data}")

    try:
        # Insert data into PostgreSQL
        cursor.execute("""
            INSERT INTO patient_vitals (hadm_id, HR, TEMP, SPO2, masktype, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['hadm_id'], data['HR'], data['TEMP'], data['SPO2'], data['masktype'], data['timestamp']))
        
        conn.commit()
        print("YAYY Data inserted into PostgreSQL successfully! <3 <3 <3")
    except Exception as e:
        print(f"Error inserting data into PostgreSQL: {e} WOMP WOMP WOMP")
        conn.rollback()
