import dash
from dash import html, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
from flask import request, jsonify
import json
import io
import base64

# Import our custom modules
from db import init_database, add_entry_to_db, clear_all_entries
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
    
    # Control buttons
    html.Div([
        html.H3("Controls"),
        html.Div([
            html.Button(
                "🔄 Force Refresh", 
                id="refresh-btn", 
                n_clicks=0,
                style={"marginRight": "10px", "padding": "10px 20px", "backgroundColor": "#007bff", "color": "white", "border": "none", "borderRadius": "5px", "cursor": "pointer"}
            ),
            html.Button(
                "📥 Download CSV", 
                id="download-btn", 
                n_clicks=0,
                style={"marginRight": "10px", "padding": "10px 20px", "backgroundColor": "#28a745", "color": "white", "border": "none", "borderRadius": "5px", "cursor": "pointer"}
            ),
            html.Button(
                "🗑️ Clear All Data", 
                id="clear-btn", 
                n_clicks=0,
                style={"padding": "10px 20px", "backgroundColor": "#dc3545", "color": "white", "border": "none", "borderRadius": "5px", "cursor": "pointer"}
            ),
        ], style={"display": "flex", "gap": "10px"}),
        html.Div(id="button-output", style={"marginTop": "10px", "color": "green"}),
    ], style={"margin": "20px", "padding": "20px", "backgroundColor": "#f8f9fa", "borderRadius": "5px"}),
    
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
        interval=10000,  # Update every 10 second
        n_intervals=0
    ),
    
    # Download component for CSV
    dcc.Download(id="download-csv")
])

# Callback to update the grid (responds to both interval and refresh button)
@callback(
    Output("user-grid", "rowData"),
    [Input("interval-component", "n_intervals"),
     Input("refresh-btn", "n_clicks")]
)
def update_grid(n_intervals, refresh_clicks):
    print("Refreshing grid from database")
    return prepare_data_for_grid()

# Callback for CSV download
@callback(
    Output("download-csv", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_csv(n_clicks):
    if n_clicks > 0:
        data = prepare_data_for_grid()
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "user_entries.csv", index=False)

# Callback for clear data button
@callback(
    Output("button-output", "children"),
    Input("clear-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_database(n_clicks):
    if n_clicks > 0:
        if clear_all_entries():
            return "✅ Database cleared successfully!"
        else:
            return "❌ Failed to clear database"
    return ""

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