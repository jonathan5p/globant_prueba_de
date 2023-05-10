Implemented architecture for the Globant Data Enginneer interview test.

[Arquitecture Diagram](./images/GlobantArq.pdf)

# Prerequisites!

For CDK and permissions:

* CDK Version 2

* Create a CDK deployment role (you can also use the one created by cdk when doing bootstrapping, but it is recomended to create a custom role just for CDK usage)

* Create a secret named github-token in secrets manager with the github access token for the CICD pipeline. Without this secret the pipeline can't get trigger by github events. 
# Implementation details
Relevant details about the implementation.

## App Configuration yaml 

The **configs.yaml** file stored in the **config_files** folder of this project defines the configuration of the app. This file is splitted into three parts; one with all the parameters related to the environment, one with all the tags required for the deployed resources, and the last one for the configuration parameters of all the stacks to be deployed. 

When defining a new stack configuration, it is expected that this new config section will have the same name as the stack to which it belongs. Otherwise, the stack to stack_config assignment will not be carried out properly and the application will present errors when being synthesized or deployed.

# Basic shell commands for CDK

By default CDK will use the default role created at bootstrap of the environment to synth/deploy/destroy all the stacks in the app. However, using different flags we can use a specific role to synth/deploy/destroy a given stack.

```bash
$ cdk bootstrap [-c @aws-cdk/core:newStyleStackSynthesis=true] [--cloudformation-execution-policies arn:aws:iam::aws:policy/PolicyName] aws://ACCOUNT-NUMBER/REGION
$ cdk [--role-arn <CDK_ROLE_ARN>] synth [<STACK_NAME> or --all to synthetize all the stacks]
$ cdk [--role-arn <CDK_ROLE_ARN>] deploy [<STACK_NAME> or --all to deploy all the stacks]
$ cdk [--role-arn <CDK_ROLE_ARN>] destroy [<STACK_NAME> or --all to destroy all the stacks]
```

# Stacks available

* **NetworkingStack**: All the necessary resources to test the api deployment in a secure environment.
* **RdsStack**: Test MySQL database and bastion host.
* **GlobantPruebaStack**: Main application stack. It contains the API, Lambda functions and S3 buckets necessary for the application to work properly. 

# Sections 

Section by sections solutions explained. 

Before reviewing what has been done in each section, I would like to make a clarification,ue to the amount and volume of the data used in this test, I recommend to use the [aws pandas sdk](https://aws-sdk-pandas.readthedocs.io/en/stable/) that 
is an AWS Professional Service open source python initiative that extends the power of the pandas library to AWS, connecting DataFrames and AWS data & analytics services.

Built on top of other open-source projects like Pandas, Apache Arrow and Boto3, it offers abstracted functions to execute your usual ETL tasks like load/unloading data from Data Lakes, Data Warehouses and Databases, even at scale.

If the volume of data reaches a point where it cannot be handled by the aws pandas sdk and lambda functions, it is recommended to create a processing pipeline with pyspark on top of AWS Glue. 
## Section 1

The API receives historical csv files up to 10MB in the **POST db_migration** endpoint. The enpoint needs the parameters table, schema and append to upload the data to the database. 

+ The CSV files are store in the local storage of the requester.
+ For the purpose of this test, I used an Aurora MySQL database hosted in the AWS Cloud. 

## Section 2

The endpoint for the first sql requirement is **GET first_sql_requirement** and for the second one is **GET second_sql_requirement**. If everything is processed correctly the API returns a S3 presigned url to download a csv report with the information needed. By default the presigned url expires in 24 hours, but this can be change in the the stacks configuration file.

## Bonus track

1. All the infrastructure use for this test is hosted in the AWS public cloud and can be modified using IaC and CICD pipelines created by this repo. Another relevant point is that all the main services (the ones use by the API and not just for test purposes) are serverless services, which means that you only pay for what you use. 

2. You can find a simple API test for the db_migration endpoint in the file *tests/api_tests/db_migration_tests.py*. In a production environment this test should be added to the CICD pipeline as a integration test for the application after we deployed.

3. In this case we don't need to containerize the application, but if it is needed we can use FastAPI, Docker and EC2 or Lambda to host this API in the AWS Cloud.

