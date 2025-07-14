# Example Dash Application with Auto-Logging

This directory contains a sample Dash application that demonstrates how to integrate the `dash_auto_logger.py` module into any existing Dash app.

## Overview

The example app shows a simple Dash application with:
- Interactive dropdown component
- Auto-logging functionality that reports user activity every 5 seconds
- Proper integration with the receiver service

## Files

- `app.py`: Main Dash application with auto-logging integration
- `dash_auto_logger.py`: Copy of the logging module (must be in the same directory)
- `requirements.txt`: Required dependencies for the example app
- `Procfile`: Configuration for deployment

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in this directory with the following variables:

```env
DEURL=your-dash-enterprise5-url
USERNAME=your-username
PASSWORD=your-password
```

These must be valid credentials for the DE5 instance.

### 3. Update Server URL

In `app.py`, update the `server_url` parameter to point to your deployed receiver application:

```python
setup_auto_logging(app, server_url="https://your-receiver-app.plotly.host/listener-app", interval_seconds=5)
```

### 4. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:8050`.