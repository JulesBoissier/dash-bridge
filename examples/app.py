"""
Example Dash App with Auto-Logging

This example demonstrates how to use the dash_auto_logger module
to add automatic logging functionality to any Dash application.
"""

import dash
from dash import html, dcc, Input, Output, callback

# Import the auto-logging module
from dash_auto_logger import setup_auto_logging

# Initialize the Dash app
app = dash.Dash(__name__)

server = app.server

# Define your app layout as usual
app.layout = html.Div([
    html.H1("Simple Dash App with Auto-Logging"),
    html.Div([
        html.H2("Main App Content"),
        html.P("This is your regular Dash app content. The auto-logging functionality will be added automatically below."),
        
        # Some interactive components for demonstration
        html.Div([
            html.H3("Interactive Demo"),
            html.Label("Select a value:"),
            dcc.Dropdown(
                id="demo-dropdown",
                options=[
                    {"label": "Option 1", "value": "opt1"},
                    {"label": "Option 2", "value": "opt2"},
                    {"label": "Option 3", "value": "opt3"},
                ],
                value="opt1"
            ),
            html.Div(id="demo-output", style={"marginTop": "20px", "padding": "10px", "backgroundColor": "#e9ecef", "borderRadius": "5px"})
        ], style={"margin": "20px", "padding": "20px", "backgroundColor": "#f8f9fa", "borderRadius": "5px"}),
    ])
])

# Regular callback for your app functionality
@callback(
    Output("demo-output", "children"),
    Input("demo-dropdown", "value")
)
def update_demo_output(selected_value):
    return f"You selected: {selected_value}"

if __name__ == "__main__":
    # Add auto-logging functionality with just one line!
    # This will automatically:
    # 1. Add logging UI components to your app
    # 2. Set up interval-based logging every 3 seconds
    # 3. Use environment variables for configuration
    
    setup_auto_logging(app, interval_seconds=5)
    
    # You can also customize the behavior:
    # setup_auto_logging(
    #     app,
    #     server_url="http://localhost:8050",  # Custom receiver URL
    #     interval_seconds=5,                  # Log every 5 seconds
    # )
    
    # Run the app
    app.run_server(debug=True) 