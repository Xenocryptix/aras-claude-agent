"""
Authentication module for Aras Innovator API access
Created by D. Theoden
Date: June 12, 2025
"""

import requests
from .config import URL, USERNAME, PASSWORD, DATABASE

# Module-level token storage
_token = None


def authenticate():
    """Authenticate with Aras Innovator server using OAuth 2.0 and store the token.
    
    Gets a Bearer token using the Resource Owner Password Credentials Grant.
    The token is stored as a module-level variable for use by other scripts.
    This method is also used for reauthentication.
    
    Returns:
        str: The access token if successful
        
    Raises:
        ValueError: If required environment variables are not set
        requests.exceptions.HTTPError: If the authentication request fails
    """
    global _token
    
    # Validate required variables
    if not URL:
        raise ValueError("API_URL is not set. Check your environment variables or .env file")
    if not USERNAME:
        raise ValueError("API_USERNAME is not set. Check your environment variables or .env file")
    if not PASSWORD:
        raise ValueError("API_PASSWORD is not set. Check your environment variables or .env file")
    if not DATABASE:
        raise ValueError("ARAS_DATABASE is not set. Check your environment variables or .env file")
    
    token_url = f"{URL}/oauthserver/connect/token"
    
    # Prepare OAuth 2.0 token request
    token_data = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "database": DATABASE,
        "scope": "openid Innovator offline_access",
        "client_id": "IOMApp"
    }
    
    # Make token request
    response = requests.post(
        token_url,
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    response.raise_for_status()
    _token = response.json()["access_token"]
    return _token


def test_token():
    """Test connection using the current stored token.
    
    Makes a lightweight API call to verify the token is valid.
    
    Returns:
        bool: True if the token is valid, False otherwise
    """
    global _token
    
    if not _token:
        return False
    
    try:
        test_url = f"{URL}/Server/Odata/$metadata"
        response = requests.get(
            test_url,
            headers={
                'Authorization': f'Bearer {_token}',
                'Accept': 'application/json'
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def get_token():
    """Get the current stored token.
    
    Returns:
        str: The current token, or None if not authenticated
    """
    return _token


def set_token(token):
    """Set the stored token (used by APIClient for token management).
    
    Args:
        token: The token to store
    """
    global _token
    _token = token