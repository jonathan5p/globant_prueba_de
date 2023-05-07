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
    tables = wr.mysql.read_sql_query(sql="show tables;",con=con)
    if table in tables.iloc[:,0].to_list():
        with con.cursor() as cursor:
            cursor.execute(f"DROP TABLE {table}")
    wr.mysql.to_sql(df=data_df, table=table, schema=schema, con=con)
    con.close()
    

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    if event["headers"].get("Content-Type") == "text/csv":
        df = _read_csv(event.get("body"))
        table = event.get("queryStringParameters").get("table")
        schema = event.get("queryStringParameters").get("schema")

        print("Table: ", table)
        print("Schema: ", schema)

        _send_data_to_mysql(data_df=df, table=table, schema=schema)

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}

    res["body"] = f"Data loaded succesfully!"
    return res
