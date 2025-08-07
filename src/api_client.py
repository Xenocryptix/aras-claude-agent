"""
Generic API Client for RESTful operations
Created by D. Theoden
Date: June 12, 2025
"""

import requests
import json
import logging
from .auth import get_bearer_token
from .config import URL

class APIClient:
    def __init__(self):
        self.token = None
        self.url = URL
        self.odata_url = f"{URL}/Server/Odata"  # Aras OData endpoint

    def authenticate(self):
        """Authenticate with the API and store the token."""
        try:
            self.token = get_bearer_token()
            logging.info(f"✅ Successfully authenticated with Aras API server: {self.url}")
            return True
        except Exception as error:
            import sys
            print(f"Authentication error: {error}", file=sys.stderr)
            logging.error(f"❌ Authentication failed with Aras API server: {self.url} - {error}")
            return False

    def get_items(self, endpoint, expand=None, filter_param=None, select=None):
        """Get items from Aras OData API."""
        try:
            if not self.token:
                self.authenticate()

            # Build OData URL - endpoint should be an ItemType like 'Part', 'Document', etc.
            api_url = f"{self.odata_url}/{endpoint}"
            params = []
            
            if expand:
                params.append(f"$expand={expand}")
            if filter_param:
                params.append(f"$filter={filter_param}")
            if select:
                params.append(f"$select={select}")
            
            if params:
                api_url += "?" + "&".join(params)

            response = requests.get(
                api_url,
                headers={
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            import sys
            print(f"Error getting items: {error}", file=sys.stderr)
            raise error

    def create_item(self, endpoint, data):
        """Create a new item using Aras OData API."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.post(
                f"{self.odata_url}/{endpoint}",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            import sys
            print(f"Error creating item: {error}", file=sys.stderr)
            raise error

    def update_item(self, endpoint, item_id, data):
        """Update an existing item using Aras OData API."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.patch(
                f"{self.odata_url}/{endpoint}('{item_id}')",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            import sys
            print(f"Error updating item: {error}", file=sys.stderr)
            raise error

    def call_method(self, method_name, data):
        """Call an Aras server method."""
        try:
            if not self.token:
                self.authenticate()

            # Aras methods are typically called via OData actions
            response = requests.post(
                f"{self.odata_url}/Method('{method_name}')",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            import sys
            print(f"Error calling method {method_name}: {error}", file=sys.stderr)
            raise error

    def get_list(self, list_id, expand=None):
        """Get list data from Aras API."""
        try:
            if not self.token:
                self.authenticate()

            # Aras lists are accessed via List ItemType
            list_url = f"{self.odata_url}/List('{list_id}')"
            if expand:
                list_url += f"?$expand={expand}"

            response = requests.get(
                list_url,
                headers={
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            import sys
            print(f"Error getting list {list_id}: {error}", file=sys.stderr)
            raise error 
    
    def create_relationship(self, source_item_id, related_item_id, relationship_type, data=None):
        """Create a relationship between two items in Aras."""
        try:
            if not self.token:
                self.authenticate()

            # Prepare relationship data
            relationship_data = {
                "source_id": source_item_id,
                "related_id": related_item_id,
                **(data or {})  # Include any additional relationship properties
            }

            # Create the relationship via OData - relationships are typically created
            # by adding to the relationship ItemType (e.g., Part BOM, Document File, etc.)
            response = requests.post(
                f"{self.odata_url}/{relationship_type}",
                json=relationship_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return response.json()
        except Exception as error:
            import sys
            print(f"Error creating relationship: {error}", file=sys.stderr)
            raise error

    def delete_relationship(self, relationship_type, relationship_id):
        """Delete a relationship between two items in Aras.
        
        Args:
            relationship_type: The relationship ItemType (e.g., 'Part BOM', 'Document File')
            relationship_id: The ID of the specific relationship record to delete
        """
        try:
            if not self.token:
                self.authenticate()

            # Delete the relationship via OData DELETE operation
            response = requests.delete(
                f"{self.odata_url}/{relationship_type}('{relationship_id}')",
                headers={
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            return {"status": "success", "message": f"Relationship {relationship_id} deleted successfully"}
        except Exception as error:
            import sys
            print(f"Error deleting relationship: {error}", file=sys.stderr)
            raise error