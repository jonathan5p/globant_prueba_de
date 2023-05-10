import json
import os
from io import StringIO
import awswrangler as wr
import pandas as pd

secret_name = os.environ["secret_name"]


def _check_input_parameters(event: dict):
    res = None

    query_parameters = event.get("queryStringParameters")

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
    elif event.get("body") == None:
        res = {
            "statusCode": 400,
            "body": "Cannot find data to upload",
            "headers": {"Content-Type": "*/*"},
        }

    return res


def _read_csv(payload_body: str):
    csv_data = StringIO(payload_body)
    df = pd.read_csv(csv_data, sep=",", engine="pyarrow")
    return df


def _send_data_to_mysql(
    data_df: pd.DataFrame, table: str, schema: str, append: bool = False
):
    con = wr.mysql.connect(secret_id=secret_name)
    tables = wr.mysql.read_sql_query(sql="show tables;", con=con)
    if table in tables.iloc[:, 0].to_list() and not append:
        with con.cursor() as cursor:
            cursor.execute(f"DROP TABLE {table}")
    wr.mysql.to_sql(df=data_df, table=table, schema=schema, con=con)
    con.close()


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}
    res["body"] = f"Data loaded succesfully!"

    chk_params = _check_input_parameters(event)

    if event["headers"].get("Content-Type") == "text/csv" and chk_params == None:
        df = _read_csv(event.get("body"))

        if df.shape[0] > 1000:
            res = {
                "statusCode": 400,
                "body": f"Batch insert available for files from 1 up to 1000 rows. The file provided has {df.shape[0]} rows.",
                "headers": {"Content-Type": "*/*"},
            }
        else:
            table = event.get("queryStringParameters").get("table")
            schema = event.get("queryStringParameters").get("schema")
            append = event.get("queryStringParameters").get("append", False) == "true"

            print("Table: ", table)
            print("Schema: ", schema)
            print("Append: ", append)

            _send_data_to_mysql(data_df=df, table=table, schema=schema, append=append)

    elif chk_params != None:
        res = chk_params

    return res
