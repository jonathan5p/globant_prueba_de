import json
import os
from io import StringIO
import awswrangler as wr
import pandas as pd

secret_name = os.environ["secret_name"]

def _read_csv(payload_body: str):
    csv_data = StringIO(payload_body)
    df = pd.read_csv(csv_data, sep=",", engine="pyarrow")
    return df


def _send_data_to_mysql(data_df: pd.DataFrame, table: str, schema: str):
    con = wr.mysql.connect(secret_id=secret_name)
    wr.mysql.to_sql(df=data_df, table=table, schema=schema, con=con)
    con.close()


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    if event["headers"].get("Content-Type") == "text/csv":
        df = _read_csv(event.get("body"))
        _send_data_to_mysql(data_df=df, table="departments", schema="test_db")

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}

    res["body"] = f"Data loaded succesfully!"
    return res
