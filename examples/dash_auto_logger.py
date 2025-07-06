"""
Dash Auto Logger - A minimalistic module for adding automatic logging to Dash apps

This module provides functionality to automatically log user activity from Dash apps
to a remote receiver service with Keycloak authentication.
"""

import dash
from dash import dcc, Input, Output, callback
import requests
import time
import os
import base64
from keycloak import KeycloakOpenID
import dash_enterprise_auth as auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_keycloak_tokens():
    """Get Keycloak tokens for authentication"""
    try:
        DEURL = os.environ.get("DEURL")
        username = os.environ.get("USERNAME")
        password = os.environ.get("PASSWORD")

        print("GOT CREDS")

        if not all([DEURL, username, password]):
            raise EnvironmentError("Missing required env variables: DEURL, USERNAME, PASSWORD")

        keycloak_url = f"https://auth-{DEURL}/auth/"
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url, 
            client_id="dash", 
            realm_name="dash"
        )

        token_response = keycloak_openid.token(username, password)
        print("got token")
        access_token = token_response["access_token"]
        print("parsed token")
        id_token = token_response.get("id_token", access_token)  # Fallback to access_token if no id_token
        print("got id")
        return {
            "access_token": access_token,
            "id_token": id_token
        }
        
    except Exception as e:
        print(f"[AUTO-LOGGER] Error getting Keycloak tokens: {e}")
        return None

def add_auto_logging_feature(app, server_url="https://tam.plotly.host/listener-app", interval_seconds=3):
    """
    Adds interval-based logging to a Dash app.
    
    Args:
        app: The Dash app instance
        server_url: URL of the server app to send data to
        interval_seconds: How often to send data (in seconds)
    
    Returns:
        None (modifies the app in-place)
    """
    
    # Add interval component to the existing layout
    app.layout.children.append(
        dcc.Interval(
            id="auto-log-interval",
            interval=interval_seconds * 1000,
            n_intervals=0
        )
    )
    
    # Add callback for interval-based logging
    @callback(
        Output("auto-log-interval", "n_intervals"),
        Input("auto-log-interval", "n_intervals")
    )
    def send_log_data(n_intervals):
        if n_intervals > 0:
            _send_log_data(app, server_url)
        return n_intervals

def _send_log_data(app, server_url):
    """Core function to send log data to the receiver"""
    try:
        # Get Keycloak tokens for authentication
        tokens = get_keycloak_tokens()
        if not tokens:
            print(f"[AUTO-LOGGER] Failed to get authentication tokens")
            return

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
        
        if response.status_code == 200:
            print(f"[AUTO-LOGGER] Successfully sent: {username} at {timestamp} for {app_name}")
        else:
            print(f"[AUTO-LOGGER] Failed to send data. Status: {response.status_code}")
            
    except Exception as e:
        print(f"[AUTO-LOGGER] Error sending log data: {e}")

# Convenience function for quick setup
def setup_auto_logging(app, **kwargs):
    """
    Convenience function to set up auto-logging with environment-based configuration.
    
    Args:
        app: The Dash app instance
        **kwargs: Additional arguments to pass to add_auto_logging_feature
    """
    # Get server URL from environment or use default
    DEURL = os.environ.get("DEURL", "tam.plotly.host")
    default_server_url = f"https://{DEURL}/listener-app"

    print("ADDING AUTO LOGGING")
    print(DEURL)
    
    # Set up defaults
    config = {
        "server_url": default_server_url,
        "interval_seconds": 3
    }
    
    # Update with any provided kwargs
    config.update(kwargs)
    
    # Add the auto-logging feature
    add_auto_logging_feature(app, **config) 