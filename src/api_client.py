"""
Generic API Client for RESTful operations
Created by D. Theoden
Date: June 12, 2025
"""

import requests
import json
import logging
from .auth import authenticate, test_token
from .config import URL

class APIClient:
    def __init__(self):
        self.token = None
        self.url = URL
        self.odata_url = f"{URL}/Server/Odata"  # Aras OData endpoint

    def authenticate(self):
        """Authenticate with the API and store the token."""
        try:
            self.token = authenticate()
            logging.info(f"✅ Successfully authenticated with Aras API server: {self.url}")
            return True
        except Exception as error:
            import sys
            print(f"Authentication error: {error}", file=sys.stderr)
            logging.error(f"❌ Authentication failed with Aras API server: {self.url} - {error}")
            return False

    def is_token_valid(self):
        """Check if the current token is still valid."""
        if not self.token:
            return False
        # Use the auth module's test_token which tests the stored token
        # But we need to test our local token, so we do it directly
        try:
            test_url = f"{self.url}/Server/Odata/$metadata"
            response = requests.get(
                test_url,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Accept': 'application/json'
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def ensure_valid_token(self):
        """Ensure we have a valid token, reauthenticating if necessary."""
        if not self.token:
            return self.authenticate()
        
        if not self.is_token_valid():
            logging.info("Token expired, attempting reauthentication...")
            return self.authenticate()
        
        return True

    def _make_request_with_retry(self, method, url, **kwargs):
        """Make an HTTP request with automatic token refresh on 401 errors."""
        # Ensure we have a valid token
        if not self.ensure_valid_token():
            raise Exception("Failed to obtain valid authentication token")
        
        # Add authorization header
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        # Make the request
        response = getattr(requests, method.lower())(url, **kwargs)
        
        # If we get a 401, try to reauthenticate once and retry
        if response.status_code == 401:
            logging.info("Received 401 error, attempting reauthentication...")
            if self.authenticate():
                # Update the authorization header with new token
                headers['Authorization'] = f'Bearer {self.token}'
                kwargs['headers'] = headers
                # Retry the request
                response = getattr(requests, method.lower())(url, **kwargs)
            else:
                raise Exception("Failed to reauthenticate after 401 error")
        
        response.raise_for_status()
        return response

    def get_items(self, endpoint, expand=None, filter_param=None, select=None):
        """Get items from Aras OData API."""
        try:
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

            response = self._make_request_with_retry(
                'GET',
                api_url,
                headers={
                    'Accept': 'application/json'
                }
            )

            return response.json()
        except Exception as error:
            import sys
            print(f"Error getting items: {error}", file=sys.stderr)
            raise error

    def create_item(self, endpoint, data):
        """Create a new item using Aras OData API."""
        try:
            response = self._make_request_with_retry(
                'POST',
                f"{self.odata_url}/{endpoint}",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            return response.json()
        except Exception as error:
            import sys
            print(f"Error creating item: {error}", file=sys.stderr)
            raise error

    def update_item(self, endpoint, item_id, data):
        """Update an existing item using Aras OData API."""
        try:
            response = self._make_request_with_retry(
                'PATCH',
                f"{self.odata_url}/{endpoint}('{item_id}')",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            return response.json()
        except Exception as error:
            import sys
            print(f"Error updating item: {error}", file=sys.stderr)
            raise error

    def call_method(self, method_name, data):
        """Call an Aras server method."""
        try:
            # Aras methods are typically called via OData actions
            response = self._make_request_with_retry(
                'POST',
                f"{self.odata_url}/Method('{method_name}')",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            return response.json()
        except Exception as error:
            import sys
            print(f"Error calling method {method_name}: {error}", file=sys.stderr)
            raise error

    def get_list(self, list_id, expand=None):
        """Get list data from Aras API."""
        try:
            # Aras lists are accessed via List ItemType
            list_url = f"{self.odata_url}/List('{list_id}')"
            if expand:
                list_url += f"?$expand={expand}"

            response = self._make_request_with_retry(
                'GET',
                list_url,
                headers={
                    'Accept': 'application/json'
                }
            )

            return response.json()
        except Exception as error:
            import sys
            print(f"Error getting list {list_id}: {error}", file=sys.stderr)
            raise error 

    def get_latest_item(self, item_type, config_id):
        """Get the latest ID of an item by its config_id.
        
        Args:
            item_type: The ItemType to query (e.g., 'Part', 'Document')
            config_id: The config_id to filter by
            
        Returns:
            str: The ID of the latest item with the specified config_id
        """
        try:
            # Build OData URL with filter for config_id
            api_url = f"{self.odata_url}/{item_type}?$filter=(config_id eq '{config_id}' and is_current eq 1)"
            
            response = self._make_request_with_retry(
                'GET',
                api_url,
                headers={
                    'Accept': 'application/json'
                }
            )
            
            result = response.json()
            
            # Check if we got any results
            if not result.get('value') or len(result['value']) == 0:
                raise ValueError(f"No item found with config_id '{config_id}' in ItemType '{item_type}'")
            
            # Return the ID of the first (latest) item
            item_id = result['value'][0]['id']
            logging.info(f"✅ Found latest item ID: {item_id} for config_id: {config_id} in {item_type}")
            return item_id
            
        except Exception as error:
            import sys
            print(f"Error getting latest item: {error}", file=sys.stderr)
            logging.error(f"❌ Error getting latest item for config_id '{config_id}' in '{item_type}': {error}")
            raise error
    
    def create_relationship(self, source_item_id, related_item_id, relationship_type, data=None):
        """Create a relationship between two items in Aras."""
        try:
            # Prepare relationship data
            relationship_data = {
                "source_id": source_item_id,
                "related_id": related_item_id,
                **(data or {})  # Include any additional relationship properties
            }

            # Create the relationship via OData - relationships are typically created
            # by adding to the relationship ItemType (e.g., Part BOM, Document File, etc.)
            response = self._make_request_with_retry(
                'POST',
                f"{self.odata_url}/{relationship_type}",
                json=relationship_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

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
            # Delete the relationship via OData DELETE operation
            response = self._make_request_with_retry(
                'DELETE',
                f"{self.odata_url}/{relationship_type}('{relationship_id}')",
                headers={
                    'Accept': 'application/json'
                }
            )

            return {"status": "success", "message": f"Relationship {relationship_id} deleted successfully"}
        except Exception as error:
            import sys
            print(f"Error deleting relationship: {error}", file=sys.stderr)
            raise error