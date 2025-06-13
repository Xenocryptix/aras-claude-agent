"""
Authentication module for API access
Created by D. Theoden
Date: June 12, 2025
"""

import requests
import os
from dotenv import load_dotenv
from .config import URL, USERNAME, PASSWORD

# Load environment variables
load_dotenv()

def get_bearer_token():
    """Get bearer token for API authentication."""
    try:
        # Basic authentication to get token
        auth_data = {
            "username": USERNAME,
            "password": PASSWORD
        }

        token_res = requests.post(
            f"{URL}/auth/token",
            json=auth_data,
            headers={'Content-Type': 'application/json'}
        )
        token_res.raise_for_status()

        return token_res.json()["access_token"]
    except Exception as err:
        print(f"Error in get_bearer_token: {err}")
        raise err 