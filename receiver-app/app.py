import dash
from dash import html, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
from flask import request, jsonify
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__)

server = app.server

# Database connection
connection_string = os.environ.get("DATABASE_URL", "postgresql://postgres:docker@127.0.0.1:5432")

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database table if it doesn't exist"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_entries (
                    id SERIAL PRIMARY KEY,
                    app_name VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    timestamp VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Database table initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            cur.close()
            conn.close()

def get_all_entries():
    """Get all entries from database"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT app_name, username, timestamp FROM user_entries ORDER BY created_at DESC")
            entries = cur.fetchall()
            return [dict(entry) for entry in entries]
        except Exception as e:
            print(f"Error fetching entries: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    return []

def add_entry_to_db(app_name, username, timestamp):
    """Add entry to database"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO user_entries (app_name, username, timestamp) VALUES (%s, %s, %s)",
                (app_name, username, timestamp)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding entry to database: {e}")
            return False
        finally:
            cur.close()
            conn.close()
    return False

# Initialize database on startup
init_database()

# Define the AG Grid column definitions
columnDefs = [
    {"headerName": "App Name", "field": "app_name", "sortable": True, "filter": True},
    {"headerName": "Username", "field": "username", "sortable": True, "filter": True},
    {"headerName": "Timestamp", "field": "timestamp", "sortable": True, "filter": True},
    {"headerName": "Readable Time", "field": "readable_time", "sortable": True, "filter": True},
]

def convert_timestamp_to_readable(timestamp_str):
    """Convert timestamp to readable format"""
    try:
        # Assume timestamp is in milliseconds
        timestamp = int(timestamp_str) / 1000
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Invalid timestamp"

def prepare_data_for_grid():
    """Prepare data with readable timestamps from database"""
    entries = get_all_entries()
    prepared_data = []
    for item in entries:
        prepared_item = item.copy()
        prepared_item["readable_time"] = convert_timestamp_to_readable(item["timestamp"])
        prepared_data.append(prepared_item)
    return prepared_data

# Define the layout
app.layout = html.Div([
    html.H1("User Logging Dashboard", style={"textAlign": "center", "marginBottom": "20px"}),
    
    html.Div([
        html.H3("API Endpoint Information"),
        html.P("Send POST requests to: /api/add_entry"),
        html.P("Expected JSON format: {\"app_name\": \"my_app\", \"username\": \"username1\", \"timestamp\": \"12125313254213\"}"),
        html.Hr(),
    ], style={"margin": "20px", "padding": "20px", "backgroundColor": "#f0f0f0", "borderRadius": "5px"}),
    
    html.Div([
        html.H3("User Entries"),
        dag.AgGrid(
            id="user-grid",
            columnDefs=columnDefs,
            rowData=prepare_data_for_grid(),
            defaultColDef={"resizable": True, "sortable": True, "filter": True},
            style={"height": "400px", "width": "100%"},
            dashGridOptions={"pagination": True, "paginationPageSize": 10},
        ),
    ], style={"margin": "20px"}),    
    # Interval component for auto-refresh
    dcc.Interval(
        id="interval-component",
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    )
])

# Callback to update the grid
@callback(
    Output("user-grid", "rowData"),
    Input("interval-component", "n_intervals")
)
def update_grid(n_intervals):
    print("Refreshing grid from database")
    return prepare_data_for_grid()

# Add Flask route for receiving JSON data
@app.server.route(app.config.routes_pathname_prefix + "api/add_entry", methods=["POST"])
def add_entry():
    print("RECEIVED SOMETHING")
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data or "app_name" not in data or "username" not in data or "timestamp" not in data:
            return jsonify({"error": "Missing required fields: app_name, username, timestamp"}), 400
        
        # Add the entry to database
        if add_entry_to_db(data["app_name"], data["username"], str(data["timestamp"])):
            return jsonify({"message": "Entry added successfully"}), 200
        else:
            return jsonify({"error": "Failed to add entry to database"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run_server(debug=True) 