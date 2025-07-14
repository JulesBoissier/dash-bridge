# Receiver Application - Centralized Logging Service

The receiver application is a centralized service that collects and stores user activity logs from multiple Dash applications. It provides a web-based dashboard for viewing, managing, and exporting logging data.

## Overview

This application serves as the central hub for collecting user activity data from Dash applications that have integrated the `dash_auto_logger.py` module. It stores all logging data in a PostgreSQL database and provides a web interface for data management.

## Features

- **REST API**: Accepts POST requests from logging-enabled Dash apps
- **PostgreSQL Integration**: Stores logging data in a relational database
- **Web Dashboard**: Interactive AG Grid interface for viewing logged data
- **Real-time Updates**: Automatic data refresh every 30 seconds
- **Export Functionality**: Download logging data as CSV files
- **Database Management**: Clear all entries with a single click
- **Responsive Design**: Clean, modern web interface

## Files

- `app.py`: Main Dash application with dashboard and API endpoints
- `db.py`: Database operations and PostgreSQL integration
- `utils.py`: Utility functions for data processing
- `requirements.txt`: Required dependencies
- `Procfile`: Configuration for Dash Enterprise deployment

## Deployment on Dash Enterprise 5

### 1. Prerequisites

- Access to Dash Enterprise 5
- Ability to create and manage applications
- PostgreSQL database service capability

### 2. Deploy the Application

1. **Create a new app** in Dash Enterprise 5
2. **Upload the receiver-app code** to your DE5 app
3. **Add a PostgreSQL database**:
   - Go to the **Service Tab** in your app
   - Add a PostgreSQL database service
   - The connection details will be automatically configured

4. **Deploy the application**:
   - The app will automatically install dependencies from `requirements.txt`
   - Database tables will be created automatically on first run

### 3. Configuration

The application automatically configures itself using environment variables provided by Dash Enterprise 5. No manual configuration is required for the database connection.

### 4. Access the Dashboard

Once deployed, access your receiver app at:
```
https://de5-url.plotly.host/receiver-app
```

## API Endpoints

### POST /api/add_entry

Accepts logging data from Dash applications.

**Request Format**:
```json
{
  "app_name": "my_dash_app",
  "username": "user123",
  "timestamp": "1640995200000"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Entry added successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message"
}
```

## Database Schema

The application creates a `usage_logs` table with the following structure:

```sql
CREATE TABLE IF NOT EXISTS usage_logs (
    id SERIAL PRIMARY KEY,
    app_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL,
    readable_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Dependencies

The application requires the following Python packages:

```
dash==2.16.1
dash-ag-grid==31.0.1
pandas==2.1.4
flask==3.0.0
psycopg2-binary==2.9.9
gunicorn
```

## Local Development

For local development and testing:

### 1. Set up PostgreSQL

Install and configure PostgreSQL locally, then set the connection string:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:8050`.