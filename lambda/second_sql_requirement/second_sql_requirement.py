import json
import os
from io import StringIO
import awswrangler as wr
import pandas as pd

secret_name = os.environ["secret_name"]

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}

    res["body"] = f"Second SQL report!"
    return res
