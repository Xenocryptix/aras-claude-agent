"""
Generic API Client for RESTful operations
Created by D. Theoden
Date: June 12, 2025
"""

import requests
import json
from .auth import get_bearer_token
from .config import URL

class APIClient:
    def __init__(self):
        self.token = None
        self.url = URL

    def authenticate(self):
        """Authenticate with the API and store the token."""
        try:
            self.token = get_bearer_token()
            return True
        except Exception as error:
            print(f"Authentication error: {error}")
            return False

    def get_items(self, endpoint, expand=None, filter_param=None, select=None):
        """Get items from API using REST."""
        try:
            if not self.token:
                self.authenticate()

            # Build URL
            api_url = f"{URL}/{endpoint}"
            params = []
            
            if expand:
                params.append(f"expand={expand}")
            if filter_param:
                params.append(f"filter={filter_param}")
            if select:
                params.append(f"select={select}")
            
            if params:
                api_url += "?" + "&".join(params)

            response = requests.get(
                api_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            print(f"Error getting items: {error}")
            raise error

    def create_item(self, endpoint, data):
        """Create a new item using REST API."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.post(
                f"{URL}/{endpoint}",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            print(f"Error creating item: {error}")
            raise error

    def call_method(self, method_name, data):
        """Call a server method using REST API."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.post(
                f"{URL}/methods/{method_name}",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            print(f"Error calling method {method_name}: {error}")
            raise error

    def get_list(self, list_id, expand=None):
        """Get list data from API."""
        try:
            if not self.token:
                self.authenticate()

            # Build URL for List endpoint
            list_url = f"{URL}/lists/{list_id}"
            if expand:
                list_url += f"?expand={expand}"

            response = requests.get(
                list_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            print(f"Error getting list {list_id}: {error}")
            raise error 