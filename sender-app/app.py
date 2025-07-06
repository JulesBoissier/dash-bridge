import dash
from dash import html, dcc, Input, Output, callback
import requests
import time
import random
import os
import base64
from keycloak import KeycloakOpenID
import dash_enterprise_auth as auth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Simple Dash App"),
    html.Div("This is a simple div with some content.")
])

def get_keycloak_tokens():
    """Get Keycloak tokens for authentication"""
    try:
        DEURL = os.environ.get("DEURL")
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")

        if not all([DEURL, username, password]):
            raise EnvironmentError("Missing required env variables: DEURL, USERNAME, PASSWORD")

        keycloak_url = f"https://auth-{DEURL}/auth/"
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url, 
            client_id="dash", 
            realm_name="dash"
        )

        token_response = keycloak_openid.token(username, password)
        access_token = token_response["access_token"]
        id_token = token_response.get("id_token", access_token)  # Fallback to access_token if no id_token

        
        return {
            "access_token": access_token,
            "id_token": id_token
        }
        
    except Exception as e:
        print(f"[AUTH] Error getting Keycloak tokens: {e}")
        return None

def add_auto_logging_feature(app, server_url="https://tam.plotly.host/listener-app", interval_seconds=3):
    """
    Modular function that adds interval-based logging to the app.
    
    Args:
        app: The Dash app instance
        server_url: URL of the server app to send data to
        interval_seconds: How often to send data (in seconds)
    """
    
    # Add interval component to the existing layout
    app.layout.children.extend([
        html.Hr(),
        html.Div([
            html.H3("Auto-Logging Feature"),
            html.P(f"Sending authenticated data to {server_url}/api/add_entry every {interval_seconds} seconds"),
            html.P("🔐 Using Keycloak authentication with Bearer token + cookies"),
            html.Div(id="status-display", children="Ready to start logging...")
        ], style={"margin": "20px", "padding": "20px", "backgroundColor": "#f8f9fa", "borderRadius": "5px"}),
        
        dcc.Interval(
            id="auto-log-interval",
            interval=interval_seconds * 1000,
            n_intervals=0
        )
    ])
    
    # Add callback for interval-based logging
    @callback(
        Output("status-display", "children"),
        Input("auto-log-interval", "n_intervals")
    )
    def send_log_data(n_intervals):
        if n_intervals == 0:
            return "Ready to start logging..."
        
        try:
            # Get Keycloak tokens for authentication
            tokens = get_keycloak_tokens()
            if not tokens:
                return f"Failed to get authentication tokens (Interval #{n_intervals})"
            
            # Generate data to send
            app_name = app.config.requests_pathname_prefix
            username = auth.get_username()
            timestamp = str(int(time.time() * 1000))
            
            data = {
                "app_name": app_name,
                "username": username,
                "timestamp": timestamp
            }
            
            # Prepare headers and cookies with authentication tokens
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {tokens['access_token']}"
            }
            
            # Encode tokens as base64 for cookies (like Plotly does)
            access_token_b64 = base64.b64encode(tokens['access_token'].encode()).decode()
            id_token_b64 = base64.b64encode(tokens['id_token'].encode()).decode()
            
            cookies = {
                "kcToken": access_token_b64,
                "kcIdToken": id_token_b64
            }
            
            
            # Send POST request to the server app
            response = requests.post(
                f"{server_url}/api/add_entry",
                json=data,
                headers=headers,
                cookies=cookies,
                timeout=5
            )
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                return f"Successfully sent: {username} at {timestamp} for {app_name} (Interval #{n_intervals})"
            else:
                return f"Failed to send data. Status: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    # Add the auto-logging feature to the app
    # Use the listener app URL from environment or default
    DEURL = os.environ.get("DEURL", "tam.plotly.host")
    server_url = f"https://{DEURL}/listener-app"
    
    add_auto_logging_feature(app, server_url=server_url, interval_seconds=3)
    
    # Run the client app on a different port to avoid conflict
    app.run_server(debug=True)
