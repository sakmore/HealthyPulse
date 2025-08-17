# 🩺 HealthyPulse - Real-Time Patient Vitals Monitoring System

> A comprehensive healthcare monitoring solution providing real-time patient vital signs tracking with intelligent anomaly detection and intuitive visualization.

HealthyPulse is a robust patient vitals monitoring system built with modern data engineering technologies including Flask APIs, Apache Kafka streaming, Apache Airflow orchestration, PostgreSQL storage, and Streamlit dashboard.

## 📋 Table of Contents

- [⚡ Quick Start](#-quick-start)
- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🗄️ Database Setup](#️-database-setup)
- [🚀 Running the Project](#-running-the-project)
- [⚠️ Anomaly Detection](#️-anomaly-detection)
- [💡 Notes & Tips](#-notes--tips)

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
# Clone repository
git clone https://github.com/sakmore/HealthyPulse.git
cd HealthyPulse

# Create virtual environment
python -m venv HealthyPulse_env
source HealthyPulse_env/bin/activate  # Windows: HealthyPulse_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

Follow the [Database Setup](#️-database-setup) section below to create PostgreSQL database and tables.

### 3. Start Services

```bash
# Terminal 1: Flask Producer
python flask_producer.py

# Terminal 2: Airflow Webserver  
airflow webserver --port 8080

# Terminal 3: Airflow Scheduler
airflow scheduler

# Terminal 4: Streamlit Dashboard
streamlit run dashboard.py
```

### 4. Access Dashboard

Open `http://localhost:8501` to start monitoring! 🎉

---

## 🌟 Features
- 🚨 **Smart Anomaly Detection** - Automated alerts for critical vital sign deviations
- 📈 **Interactive Dashboard** - Clean, medical-grade interface with real-time updates
- 👥 **Patient Management** - Individual patient filtering and persistent selection
- 🔒 **Privacy Protection** - Patient IDs are hashed to maintain patient confidentiality
- 🔄 **Automated Data Pipeline** - Airflow-orchestrated data simulation and ingestion
- ⚡ **Near Real-Time Updates** - 1-second refresh rate for immediate monitoring
- 🥧 **Status Overview** - Visual distribution of stable vs anomalous patients

---

## 🏗️ Architecture

### Data Flow

```
Airflow DAG → Flask Producer → Kafka → Consumer → PostgreSQL → Streamlit Dashboard
```

### System Components

1. **Airflow (`simulate_data_dag`)** - Orchestrates data simulation by triggering Flask endpoints
2. **Flask API** - Generates realistic patient vitals in real time
3. **Kafka** - handle real-time data streaming with reliable message delivery
4. **Consumer** - Processes Kafka messages and stores data in PostgreSQL
5. **PostgreSQL** - Persistent storage with optimized indexing for fast queries
6. **Streamlit Dashboard** - Real-time visualization with automatic refresh

**Key Benefits:**
- **Scalable** - Each component can scale independently
- **Resilient** - Decoupled architecture ensures system stability
- **Real-time** - Low-latency data processing and visualization

---

## 🗄️ Database Setup

### 1. Create Database and User

```sql
-- Create database
CREATE DATABASE healthypulse_db;

-- Create dedicated user
CREATE USER healthypulse_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE healthypulse_db TO healthypulse_user;
```

### 2. Create Patient Vitals Table

```sql
-- Switch to healthypulse_db
\c healthypulse_db;

-- Create main table
CREATE TABLE patient_vitals (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    heart_rate INTEGER NOT NULL,
    temperature DECIMAL(4,2) NOT NULL,
    spo2 INTEGER NOT NULL,
    anomaly_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add performance indexes
CREATE INDEX idx_patient_vitals_patient_id ON patient_vitals(patient_id);
CREATE INDEX idx_patient_vitals_timestamp ON patient_vitals(timestamp);
CREATE INDEX idx_patient_vitals_anomaly ON patient_vitals(anomaly_type);
```

### 3. Verify Setup

```sql
-- Check table structure
\d patient_vitals;

-- Verify table is ready
SELECT COUNT(*) FROM patient_vitals;
```

---

## 🚀 Running the Project

### Prerequisites

Ensure these services are running:
- ✅ PostgreSQL server
- ✅ Apache Kafka + Zookeeper
- ✅ Python 3.8+

### Detailed Startup Process

#### 1. Flask Producer (Data Generation)
```bash
python flask_producer.py
```
- Starts on `http://localhost:5000`
- Generates patient vital signs data
- Publishes to Kafka topics when triggered

#### 2. Airflow (Orchestration)
```bash
# Initialize Airflow (first time only)
airflow db init

# Start webserver and scheduler
airflow webserver --port 8080
airflow scheduler
```
- Access UI at `http://localhost:8080`
- Enable and run `simulate_data_dag`
- Triggers Flask endpoints automatically

#### 3. Streamlit Dashboard (Visualization)
```bash
streamlit run dashboard.py
```
- Available at `http://localhost:8501`
- Auto-refreshes every second
- Displays real-time patient data

### Dashboard Features
- **Patient Selector** - Filter by specific patient or view all
- **Anomaly Alerts** - Latest 5 critical events with color coding
- **Metrics Cards** - Current statistics and patient counts
- **Trend Charts** - Time-series with normal range shading
- **Status Distribution** - Pie chart of stable vs anomalous patients

---

## ⚠️ Anomaly Detection

### Medical Thresholds

| Vital Sign | Normal Range | Anomaly Condition | Alert Type |
|------------|--------------|-------------------|------------|
| **Heart Rate** | 60-100 bpm | < 60 or > 100 | `bradycardia` / `tachycardia` |
| **Temperature** | 36.1-37.2°C | < 36.1 or > 37.2 | `hypothermia` / `hyperthermia` |
| **SpO₂** | 95-100% | < 95 | `hypoxemia` |

### Alert Severity
- 🟡 **Mild** - Slightly outside normal range
- 🟠 **Moderate** - Significant deviation  
- 🔴 **Severe** - Critical values requiring immediate attention

---

## 💡 Notes & Tips

### Performance
- Dashboard refreshes every **1 second** for real-time monitoring
- Only **latest 5 anomalies** displayed for optimal UI performance
- Database indexes ensure fast query execution

### Troubleshooting
- **No data appearing?** Check if Airflow DAG is running and triggering Flask API
- **Connection errors?** Verify PostgreSQL credentials and Kafka services
- **Slow performance?** Monitor Kafka lag and database query times

### Customization
- Modify `time.sleep(1)` in dashboard for different refresh rates
- Update anomaly thresholds in Flask producer for different patient types
- Customize Streamlit styling for institutional branding

### Security
- Use environment variables for database credentials in production
- Implement proper authentication for healthcare compliance
---

## 📸 Screenshots
<img width="1908" height="914" alt="image" src="https://github.com/user-attachments/assets/df4303dc-514b-44a1-93f6-9ecd1b9654cd" />
<img width="324" height="622" alt="image" src="https://github.com/user-attachments/assets/f9552cc8-fd74-44bc-9ec6-6bc39072f38e" />
<img width="316" height="761" alt="image" src="https://github.com/user-attachments/assets/5a29c833-2bd3-4760-a75d-6b0734754013" />
<img width="1920" height="904" alt="image" src="https://github.com/user-attachments/assets/54aba5af-2fab-4d96-87f2-53c20f9ea9ec" />
<img width="1918" height="925" alt="image" src="https://github.com/user-attachments/assets/2f2eaeb7-e758-437c-bd72-64aa5c77784e" />
<img width="1915" height="916" alt="image" src="https://github.com/user-attachments/assets/98fd0873-ff54-43c3-abfa-163169df60ad" />
<img width="1500" height="799" alt="image" src="https://github.com/user-attachments/assets/bae36f03-8d53-4945-a871-51388cf4fda8" />








---

**Built with ❤️ for healthcare monitoring**
