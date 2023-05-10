import os
import requests
import pytest
import json

headers = {
    "AWS_ACCESS_KEY": os.environ["AWS_ACCESS_KEY_ID"],
    "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
    "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
}


api_endpoint = "https://jsjmwbks88.execute-api.us-east-1.amazonaws.com/dev/"
api_method = "POST"

# Define the endpoint and parameters for each API request
endpoints = [
    {
        "name": "db_migration check schema",
        "url": "/db_migration",
        "method": "POST",
        "expected_msg":"Table and schema are required parameters"
    },
    {
        "name": "db_migration check schema",
        "url": "/db_migration",
        "method": "POST",
        "params": {"table": "departments"},
        "expected_msg":"Schema is a required parameter"
    },
    {
        "name": "db_migration check table",
        "url": "/db_migration",
        "method": "POST",
        "params": {"schema": "test_db"},
        "expected_msg":"Table is a required parameter"
    },
    {
        "name": "db_migration check data",
        "url": "/db_migration",
        "method": "POST",
        "params": {"table": "departments","schema":"test_db"},
        "expected_msg":"Cannot find data to upload"
    },
    {
        "name": "db_migration check data",
        "url": "/db_migration",
        "method": "POST",
        "params": {"table": "departments","schema":"test_db"},
        "data": "../test-files/departamentos.csv",
        "expected_msg":"Data loaded succesfully!"
    },
]

# Loop through the endpoints and make API requests
for endpoint in endpoints:
    # Build the full URL of the API request
    url = api_endpoint + endpoint["url"]

    # Make the API request
    response = None
    if "method" in endpoint and endpoint["method"] == "POST":
        if "data" in endpoint.keys():
            with open(endpoint.get("data", "")) as f:
                response = requests.post(
                    url,
                    headers=headers,
                    params=endpoint.get("params", {}),
                    files={"data.csv": f},
                )
        else:
            response = requests.post(
                    url,
                    headers=headers,
                    params=endpoint.get("params", {})
                )
    
        # Check test completion
        if response.text == endpoint.get("expected_msg",""):
            print(f"{endpoint['name']} - PASSED")
            print("Reason: ", response.text)
        else:
            print(f"{endpoint['name']} - FAILED")
            print("Reason: ", response.text)
