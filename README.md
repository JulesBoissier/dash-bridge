# Dash Auto Logger Bridge

A comprehensive solution for automatically logging user activity from Dash applications to a centralized receiver service with Keycloak authentication.

## Overview

This project provides a bridge between Dash applications and a centralized logging service, enabling automatic collection of user activity data with minimal setup. The system consists of three main components:

- **`dash_auto_logger.py`**: A lightweight module that adds automatic logging functionality to any Dash app
- **`receiver-app/`**: A centralized service that receives and stores logging data in a PostgreSQL database
- **`examples/`**: A sample Dash application demonstrating the logging integration

## Quick Start

### 1. Set up the Receiver Application

The receiver application needs to be deployed on Dash Enterprise 5 with a PostgreSQL database:

1. Deploy the `receiver-app/` to Dash Enterprise 5
2. Add a PostgreSQL database through the Service Tab in the App Manager
3. The receiver will automatically create the necessary database tables

See [receiver-app/README.md](receiver-app/README.md) for detailed deployment instructions.

### 2. Add Logging to Your Dash Apps

To enable logging in any Dash application:

1. Copy `dash_auto_logger.py` to your app directory
2. Add the following imports and setup code to your app:

```python
from dash_auto_logger import setup_auto_logging

RECEIVER_APP_URL = <Your app URL>  # URL of the App deployed in Step 1

# After creating your app instance
setup_auto_logging(app, server_url="RECEIVER_APP_URL", interval_seconds=5)
```

3. Update your `requirements.txt` with the required dependencies:

```
dash==2.16.1
requests==2.31.0
python-keycloak==3.9.1
dash-enterprise-auth
python-dotenv==1.0.0
```

### 3. Configure Environment Variables

Your logging-enabled apps need these environment variables:

```
DEURL=your-dash-enterprise5-url
USERNAME=your-username
PASSWORD=your-password
```

These must be valid credentials for the DE5 instance.

## How It Works

1. **Automatic Logging**: The `dash_auto_logger.py` module automatically adds logging components to your Dash app
2. **Periodic Reporting**: User activity is sent to the receiver service at configurable intervals (default: 5 seconds)
3. **Secure Authentication**: Uses Keycloak tokens for secure communication with the receiver
4. **Centralized Storage**: All logging data is stored in a PostgreSQL database for analysis and reporting
