import json
import os
from io import StringIO
import awswrangler as wr
import pandas as pd

secret_name = os.environ["secret_name"]


def _check_input_parameters(query_parameters: dict):
    res = None

    if query_parameters == None:
        res = {
            "statusCode": 400,
            "body": "Table and schema are required parameters",
            "headers": {"Content-Type": "*/*"},
        }
    elif "table" not in query_parameters.keys():
        res = {
            "statusCode": 400,
            "body": "Table is a required parameter",
            "headers": {"Content-Type": "*/*"},
        }
    elif "schema" not in query_parameters.keys():
        res = {
            "statusCode": 400,
            "body": "Schema is a required parameter",
            "headers": {"Content-Type": "*/*"},
        }

    return res


def _read_csv(payload_body: str):
    csv_data = StringIO(payload_body)
    df = pd.read_csv(csv_data, sep=",", engine="pyarrow")
    return df


def _send_data_to_mysql(data_df: pd.DataFrame, table: str, schema: str):
    con = wr.mysql.connect(secret_id=secret_name)
    tables = wr.mysql.read_sql_query(sql="show tables;", con=con)
    if table in tables.iloc[:, 0].to_list():
        with con.cursor() as cursor:
            cursor.execute(f"DROP TABLE {table}")
    wr.mysql.to_sql(df=data_df, table=table, schema=schema, con=con)
    con.close()


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}
    res["body"] = f"Data loaded succesfully!"

    chk_params = _check_input_parameters(event.get("queryStringParameters"))

    if event["headers"].get("Content-Type") == "text/csv" and chk_params == None:
        df = _read_csv(event.get("body"))
        table = event.get("queryStringParameters").get("table")
        schema = event.get("queryStringParameters").get("schema")

        print("Table: ", table)
        print("Schema: ", schema)

        _send_data_to_mysql(data_df=df, table=table, schema=schema)

    elif chk_params != None:
        res = chk_params

    return res
