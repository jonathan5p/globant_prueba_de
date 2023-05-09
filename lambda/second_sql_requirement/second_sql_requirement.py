import json
import os
import pandas as pd
import awswrangler as wr
import boto3

secret_name = os.environ["secret_name"]
bucket_name = os.environ["bucket_name"]
presigned_url_expiration_hours = int(os.environ["presigned_url_expiration_hours"])

s3_client = boto3.client("s3")

sql = """
            WITH hired_employees_cte AS (
                SELECT
                    dp.id,
                    dp.department,
                    COUNT(*) AS hired
                FROM
                    hired_employees AS he
                    JOIN departments AS dp ON he.department_id = dp.id
                WHERE
                    YEAR(datetime)= 2021
                GROUP BY
                    dp.department
            )
            SELECT
                *
            FROM
                hired_employees_cte AS he
            WHERE
                he.hired > (
                    SELECT AVG(hired) FROM hired_employees_cte
                )
            ORDER BY he.hired DESC;
    """


def _run_query():
    con = wr.mysql.connect(secret_id=secret_name)
    df = wr.mysql.read_sql_query(sql, con)
    con.close()
    return df


def _save_data_in_s3(data: pd.DataFrame):

    wr.s3.to_csv(
        df=data,
        index=False,
        path=f"s3://{bucket_name}/second_sql_requirement_report.csv"
    )

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": "second_sql_requirement_report.csv"},
        ExpiresIn = presigned_url_expiration_hours * 3600,
    )

    print("Upload Successful", url)
    return url


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    df = _run_query()
    url = _save_data_in_s3(data = df)

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}
    res["body"] = {"message" : f"Second SQL report runned succesfuly!",
                   "presigned-url": url}

    return res
