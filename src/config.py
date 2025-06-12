"""
Configuration module for Aras Innovator MCP Server
Created by D. Theoden (www.arasdeveloper.com)
Date: June 12, 2025
"""

import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('ARAS_URL')
DATABASE = os.getenv('ARAS_DATABASE')
USERNAME = os.getenv('ARAS_USERNAME')
PASSWORD = os.getenv('ARAS_PASSWORD') 