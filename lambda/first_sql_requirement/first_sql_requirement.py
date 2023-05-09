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
                    quarter(datetime) AS quart,
                    department_id,
                    job_id
                FROM
                    hired_employees
                WHERE
                    YEAR(datetime)= 2021
                )
                SELECT
                    dp.department,
                    jb.job,
                    sum(he.quart = 1) AS Q1,
                    sum(he.quart = 2) AS Q2,
                    sum(he.quart = 3) AS Q3,
                    sum(he.quart = 4) AS Q4
                FROM
                    hired_employees_cte AS he
                JOIN departments AS dp ON
                    he.department_id = dp.id
                JOIN jobs AS jb ON
                    he.job_id = jb.id
                GROUP BY
                    dp.id,
                    jb.id
                ORDER BY
                    dp.department,
                    jb.job DESC;
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
        path=f"s3://{bucket_name}/first_sql_requirement_report.csv"
    )

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": "first_sql_requirement_report.csv"},
        ExpiresIn= presigned_url_expiration_hours * 3600,
    )

    print("Upload Successful", url)
    return url


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    df = _run_query()
    url = _save_data_in_s3(data=df)

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}
    res["body"] = json.dumps({"message" : f"First SQL report runned succesfuly!",
                   "presigned-url": url})
    return res
