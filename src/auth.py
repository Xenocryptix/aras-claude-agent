"""
Authentication module for Aras Innovator OAuth
Created by D. Theoden (www.arasdeveloper.com)
Date: June 12, 2025
"""

import requests
from .config import URL, DATABASE, USERNAME, PASSWORD

def get_bearer_token():
    """Get OAuth bearer token for Aras Innovator authentication."""
    try:
        # Get OAuth discovery URL
        discovery_url = f"{URL}/Server/OAuthServerDiscovery.aspx"
        oauth_res = requests.get(discovery_url)
        oauth_res.raise_for_status()
        oauth_url = oauth_res.json()["locations"][0]["uri"]

        # Get endpoint configuration
        endpoint_url = f"{oauth_url}.well-known/openid-configuration"
        endpoint_res = requests.get(endpoint_url)
        endpoint_res.raise_for_status()
        token_url = endpoint_res.json()["token_endpoint"]

        # Request access token
        token_data = {
            "grant_type": "password",
            "scope": "Innovator",
            "client_id": "IOMApp",
            "username": USERNAME,
            "password": PASSWORD,
            "database": DATABASE
        }

        token_res = requests.post(
            token_url,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        token_res.raise_for_status()

        return token_res.json()["access_token"]
    except Exception as err:
        print(f"Error in get_bearer_token: {err}")
        raise err 