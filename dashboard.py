import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import OperationalError
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()  


PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DATABASE")  

@st.cache_resource
def init_connection():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        return conn
    except OperationalError as e:
        st.error(f"Failed to connect to PostgreSQL: {e}")
        st.stop()

conn = init_connection()
cursor = conn.cursor()  

@st.cache_data(ttl=1)
def get_vitals_data(time_window_minutes=60):
    query_time = datetime.now() - timedelta(minutes=time_window_minutes)
    query = f"""
        SELECT hadm_id, hr, temp, spo2, masktype, timestamp
        FROM patient_vitals
        WHERE timestamp >= '{query_time.isoformat()}'
        ORDER BY timestamp DESC;
    """
    df = pd.read_sql(query, conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def is_anomalous(row):
    return (
        row["hr"] < 50 or row["hr"] > 100 or
        row["temp"] < 95.0 or row["temp"] > 101.0 or
        row["spo2"] < 94
    )

st.set_page_config(layout="wide", page_title="Healthypulse Dashboard", page_icon="❤️‍🩹")
st.title("❤️‍🩹 Healthypulse Real-time Patient Vitals Dashboard")
st.markdown("Near real-time view of patient vitals from Kafka → PostgreSQL.")

#Sidebar
with st.sidebar:
    st.header("Dashboard Controls")
    time_window_options = {
        "Last 15 Minutes": 15,
        "Last 30 Minutes": 30,
        "Last 1 Hour": 60,
        "Last 3 Hours": 180,
        "Last 6 Hours": 360,
        "All Data": 999999
    }
    selected_time_window_label = st.selectbox(
        "Select Time Window:",
        list(time_window_options.keys())
    )
    time_window_minutes = time_window_options[selected_time_window_label]

    all_data_for_patients = get_vitals_data(time_window_minutes=time_window_minutes)
    patient_ids = sorted(all_data_for_patients['hadm_id'].unique().tolist())

    # Persistent patient selection
    if 'selected_patient_id' not in st.session_state:
        st.session_state.selected_patient_id = 'All Patients'

    st.session_state.selected_patient_id = st.selectbox(
        "Filter by Patient ID:",
        ['All Patients'] + patient_ids,
        index=(['All Patients'] + patient_ids).index(st.session_state.selected_patient_id)
                if st.session_state.selected_patient_id in patient_ids else 0
    )

    st.markdown("---")
    st.info("Dashboard auto-refreshes every 1 second.")

selected_patient_id = st.session_state.selected_patient_id

#Main
df = get_vitals_data(time_window_minutes=time_window_minutes)
if selected_patient_id != 'All Patients':
    df = df[df['hadm_id'] == selected_patient_id]

if not df.empty:
    df = df.sort_values('timestamp', ascending=True)
    df['is_anomalous'] = df.apply(is_anomalous, axis=1)

    #Top Metrics
    st.subheader("Latest Patient Vitals")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Heart Rate", f"{df['hr'].iloc[-1]} BPM")
    col2.metric("Temperature", f"{df['temp'].iloc[-1]} °F")
    col3.metric("SpO₂", f"{df['spo2'].iloc[-1]} %")
    col4.metric("Anomalies (Window)", int(df['is_anomalous'].sum()))

    #Stable vs Anomalous Pie Chart
    st.subheader("Patient Status Overview")
    total_patients = df['hadm_id'].nunique()
    total_anomalous = df[df['is_anomalous']]['hadm_id'].nunique()
    total_stable = total_patients - total_anomalous

    status_fig = px.pie(
        names=["Stable", "Anomalous"],
        values=[total_stable, total_anomalous],
        color_discrete_map={"Stable": "#4CAF50", "Anomalous": "#E57373"},
        hole=0.4
    )
    status_fig.update_traces(textinfo="value+percent", pull=[0, 0.05])
    st.plotly_chart(status_fig, use_container_width=True)

    #Compact Latest Anomalies Section (Color-coded)
    st.subheader("Latest Anomalies")

    anomaly_colors = {
        "Bradycardia": "#2196F3",  # Blue
        "Tachycardia": "#FF5722",  # Orange
        "Hypothermia": "#03A9F4",  # Light Blue
        "Fever": "#FF9800",        # Orange
        "Low SpO₂": "#F44336"      # Red
    }
    latest_anomalies = df[df['is_anomalous']].sort_values('timestamp', ascending=False).head(5)

    if not latest_anomalies.empty:
        for _, row in latest_anomalies.iterrows():
            anomalies = []
            if row['hr'] < 50: anomalies.append("Bradycardia")
            if row['hr'] > 100: anomalies.append("Tachycardia")
            if row['temp'] < 95: anomalies.append("Hypothermia")
            if row['temp'] > 101: anomalies.append("Fever")
            if row['spo2'] < 94: anomalies.append("Low SpO₂")

            # Each anomaly type gets its own colored card
            for anomaly in anomalies:
                st.markdown(
                    f"<div style='padding:12px; border-radius:8px; background-color:{anomaly_colors[anomaly]}; color:white; margin-bottom:5px;'>"
                    f"<strong>Patient {row['hadm_id']}</strong> | {row['timestamp'].strftime('%H:%M:%S')}<br>"
                    f"Anomaly: {anomaly}</div>",
                    unsafe_allow_html=True
                )
    else:
        st.success("✅ No anomalies detected in the current view.")

    #Vitals Line Charts with Normal Range
    st.subheader("Vitals Trends Over Time")
    normal_ranges = {"hr": (50, 100), "temp": (95, 101), "spo2": (94, 100)}

    for vital, label in [("hr", "Heart Rate (BPM)"), ("temp", "Temperature (°F)"), ("spo2", "SpO₂ (%)")]:
        fig = px.line(
            df, x='timestamp', y=vital, color='hadm_id',
            labels={vital: label, 'timestamp': 'Time'}
        )

        # Shaded normal range
        fig.add_traces(go.Scatter(
            x=df['timestamp'],
            y=[normal_ranges[vital][1]]*len(df),
            fill=None,
            mode='lines',
            line=dict(color='lightgrey'),
            showlegend=False
        ))
        fig.add_traces(go.Scatter(
            x=df['timestamp'],
            y=[normal_ranges[vital][0]]*len(df),
            fill='tonexty',
            mode='lines',
            line=dict(color='lightgrey'),
            name='Normal Range',
            opacity=0.2
        ))

        # Subtle anomaly markers
        anomalies = df[df['is_anomalous']]
        fig.add_scatter(
            x=anomalies['timestamp'], y=anomalies[vital],
            mode='markers',
            marker=dict(color="#E57373", size=6, opacity=0.7),
            name="Anomaly"
        )

        fig.update_layout(hovermode="x unified", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info(f"No data available for the last {selected_time_window_label}. Make sure your producer/consumer are running.")
