"""
Aras Innovator Client for RESTful API operations
Created by D. Theoden (www.arasdeveloper.com)
Date: June 12, 2025
"""

import requests
import json
from .auth import get_bearer_token
from .config import URL

class ArasClient:
    def __init__(self):
        self.token = None
        self.url = URL

    def authenticate(self):
        """Authenticate with Aras Innovator and store the token."""
        try:
            self.token = get_bearer_token()
            return True
        except Exception as error:
            print(f"Authentication error: {error}")
            return False

    def fetch_bom_structure(self, item_id):
        """Fetch BOM structure for a given item ID."""
        try:
            if not self.token:
                self.authenticate()

            body = {"id": item_id}
            response = requests.post(
                f"{URL}/Server/odata/method.aer_dcm_fetchBOMStructure",
                json=body,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            response.raise_for_status()

            data = response.json()
            if data and "Item" in data:
                return self.transform_item(data["Item"])
            return []
        except Exception as error:
            print(f"Error fetching BOM Structure: {error}")
            raise error

    def transform_item(self, item, parent_id=None):
        """Transform Aras item data into a flat structure."""
        transformed = {
            "id": item.get("@aras.id"),
            "item_number": item.get("item_number"),
            "aer_title": self._extract_aer_title(item.get("aer_title")),
            "aer_major_rev": item.get("aer_major_rev"),
            "parentId": parent_id
        }
        
        result = [transformed]
        
        if item.get("Relationships") and item["Relationships"].get("Item"):
            rels = item["Relationships"]["Item"]
            if not isinstance(rels, list):
                rels = [rels]
            
            for rel in rels:
                if rel.get("related_id") and rel["related_id"].get("Item"):
                    children = self.transform_item(
                        rel["related_id"]["Item"], 
                        item.get("@aras.id")
                    )
                    result.extend(children)
        
        return result

    def _extract_aer_title(self, aer_title):
        """Extract aer_title value handling different formats."""
        if aer_title and isinstance(aer_title, dict):
            if aer_title.get("@aras.is_null"):
                return None
            return aer_title.get("@aras.keyed_name")
        return aer_title

    def execute_aml(self, aml):
        """Execute custom AML query against Aras Innovator."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.post(
                f"{URL}/Server/soap",
                data=aml,
                headers={
                    'Content-Type': 'text/xml',
                    'Authorization': f'Bearer {self.token}',
                    'SOAPAction': 'ApplyAML'
                }
            )
            response.raise_for_status()

            return response.text
        except Exception as error:
            print(f"Error executing AML: {error}")
            raise error

    def get_items(self, item_type, expand=None, filter_param=None, select=None):
        """Get items from Aras using OData API."""
        try:
            if not self.token:
                self.authenticate()

            # Build OData URL
            odata_url = f"{URL}/Server/odata/{item_type}"
            params = []
            
            if expand:
                params.append(f"$expand={expand}")
            if filter_param:
                params.append(f"$filter={filter_param}")
            if select:
                params.append(f"$select={select}")
            
            if params:
                odata_url += "?" + "&".join(params)

            response = requests.get(
                odata_url,
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

    def create_item(self, item_type, data):
        """Create a new item in Aras using OData API."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.post(
                f"{URL}/Server/odata/{item_type}",
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
        """Call an Aras server method using OData API."""
        try:
            if not self.token:
                self.authenticate()

            response = requests.post(
                f"{URL}/Server/odata/method.{method_name}",
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
        """Get list data from Aras using OData API."""
        try:
            if not self.token:
                self.authenticate()

            # Build URL for List endpoint
            list_url = f"{URL}/Server/odata/List('{list_id}')"
            if expand:
                list_url += f"?$expand={expand}"

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