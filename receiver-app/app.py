import dash
from dash import html, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
from flask import request, jsonify
import json

# Import our custom modules
from db import init_database, add_entry_to_db
from utils import prepare_data_for_grid

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Initialize database on startup
init_database()

# Define the AG Grid column definitions
columnDefs = [
    {"headerName": "App Name", "field": "app_name", "sortable": True, "filter": True},
    {"headerName": "Username", "field": "username", "sortable": True, "filter": True},
    {"headerName": "Timestamp", "field": "timestamp", "sortable": True, "filter": True},
    {"headerName": "Readable Time", "field": "readable_time", "sortable": True, "filter": True},
]

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