import json
import os
from io import StringIO
import awswrangler as wr
import pandas as pd

secret_name = os.environ["secret_name"]


def _run_query():
    con = wr.mysql.connect(secret_id=secret_name)
    with con.cursor() as cursor:
        df = cursor.execute(
            """
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
        )
        print(df.head(5))
    con.close()

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    res = {"statusCode": 200, "headers": {"Content-Type": "*/*"}}

    _run_query()

    res["body"] = f"First SQL report!"
    return res
