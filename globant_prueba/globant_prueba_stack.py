from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway as apg,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_secretsmanager as sm,
)
from constructs import Construct


class GlobantPruebaStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_config: dict,
        app_prefix: str,
        stack_config: dict,
        networking_stack: Stack,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
        self.env_config = env_config
        self.stack_config = stack_config
        self.app_prefix = app_prefix
        self.networking_stack = networking_stack
        self.main()

    def main(self):

        # =============== Resource Configurations ===============

        lambda_config = self.stack_config.get("Lambda")

        # =============== Lambda Backend ===============

        # AWS Data Wrangler layer
        wrangler_layer_arn = (
            f"arn:aws:lambda:{self.region}:336392948345:layer:AWSSDKPandas-Python39:6"
        )
        wrangler_layer_version = lambda_.LayerVersion.from_layer_version_arn(
            self, "AWSDataWranglerLayerVersion", wrangler_layer_arn
        )

        # DB Migration lambda
        lambda_env_vars = {"secret_name": lambda_config.get("secret_name")}

        db_migration_fun = lambda_.Function(
            self,
            self.app_prefix + "api-backend",
            function_name=self.app_prefix + "api-backend",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="db_migration.lambda_handler",
            code=lambda_.Code.from_asset("./lambda/db_migration"),
            environment=lambda_env_vars,
            reserved_concurrent_executions=lambda_config.get(
                "reserved_concurrent_executions"
            ),
            timeout=Duration.seconds(lambda_config.get("timeout")),
            memory_size=lambda_config.get("memory_size"),
            layers=[wrangler_layer_version],
            vpc=self.networking_stack.project_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.networking_stack.lambda_sg],
        )

        # First SQL requirement lambda
        # Number of employees hired for each job and department in 2021 divided by quarter. The
        # table must be ordered alphabetically by department and job.

        lambda_env_vars = {"secret_name": lambda_config.get("secret_name")}

        first_sql_fun = lambda_.Function(
            self,
            self.app_prefix + "first-sql-requirement",
            function_name=self.app_prefix + "first-sql-requirement",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="first_sql_requirement.lambda_handler",
            code=lambda_.Code.from_asset("./lambda/first_sql_requirement"),
            environment=lambda_env_vars,
            reserved_concurrent_executions=lambda_config.get(
                "reserved_concurrent_executions"
            ),
            timeout=Duration.seconds(lambda_config.get("timeout")),
            memory_size=lambda_config.get("memory_size"),
            layers=[wrangler_layer_version],
            vpc=self.networking_stack.project_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.networking_stack.lambda_sg],
        )

        # Second SQL requirement lambda
        # List of ids, name and number of employees hired of each department that hired more
        # employees than the mean of employees hired in 2021 for all the departments, ordered
        # by the number of employees hired (descending).

        lambda_env_vars = {"secret_name": lambda_config.get("secret_name")}

        second_sql_fun = lambda_.Function(
            self,
            self.app_prefix + "second-sql-requirement",
            function_name=self.app_prefix + "second-sql-requirement",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="second_sql_requirement.lambda_handler",
            code=lambda_.Code.from_asset("./lambda/second_sql_requirement"),
            environment=lambda_env_vars,
            reserved_concurrent_executions=lambda_config.get(
                "reserved_concurrent_executions"
            ),
            timeout=Duration.seconds(lambda_config.get("timeout")),
            memory_size=lambda_config.get("memory_size"),
            layers=[wrangler_layer_version],
            vpc=self.networking_stack.project_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.networking_stack.lambda_sg],
        )

        # =============== API Definition ===============

        api = apg.RestApi(
            self,
            self.app_prefix + "restapi",
            deploy=True,
            description="Main API for the globant test project",
            retain_deployments=False,
            binary_media_types=["multi-part/form-data"],
            default_cors_preflight_options=apg.CorsOptions(
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                ],
                allow_methods=["OPTIONS", "GET", "POST", "PUT", "PATCH", "DELETE"],
                allow_origins=["*"]
            )
        )

        # API Stages

        dev_stage = apg.Stage(
            self, 
            self.app_prefix + "api-dev-stage",
            stage_name="dev",
            deployment=api.latest_deployment,
        )

        api.deployment_stage = dev_stage

        staging_stage = apg.Stage(
            self, 
            self.app_prefix + "api-staging-stage", 
            stage_name="staging",
            deployment=api.latest_deployment,
        )

        qa_stage = apg.Stage(
            self, 
            self.app_prefix + "api-qa-stage", 
            stage_name="qa",
            deployment=api.latest_deployment,
        )

        # DB Migration endpoint
        db_migration_integration = apg.LambdaIntegration(
            handler=db_migration_fun, 
            integration_responses=[
                    {
                        "statusCode": "200",
                    },
                    {
                        "statusCode": "400",
                    },
                    {
                        "statusCode": "500",
                    },
                ]
            )

        db_migration = api.root.add_resource("db_migration")
        db_migration.add_method(
            "POST",
            integration=db_migration_integration,
            operation_name="DbMigration",
            method_responses=[
                {
                    "statusCode": "200",
                },
                {
                    "statusCode": "400",
                },
                {
                    "statusCode": "500",
                },
            ],
        )

        # First SQL requirement endpoint
        first_sql_requirement_integration = apg.LambdaIntegration(
            handler=first_sql_fun, 
            integration_responses=[
                    {
                        "statusCode": "200",
                    },
                    {
                        "statusCode": "400",
                    },
                    {
                        "statusCode": "500",
                    },
                ]
            )

        first_sql_requirement = api.root.add_resource("first_sql_requirement")
        first_sql_requirement.add_method(
            "GET",
            integration=first_sql_requirement_integration,
            operation_name="NumberOfEmployeesReport",
            method_responses=[
                {
                    "statusCode": "200",
                },
                {
                    "statusCode": "400",
                },
                {
                    "statusCode": "500",
                },
            ],
        )

        # Second SQL requirement endpoint
        second_sql_requirement_integration = apg.LambdaIntegration(
            handler=second_sql_fun, 
            integration_responses=[
                    {
                        "statusCode": "200",
                    },
                    {
                        "statusCode": "400",
                    },
                    {
                        "statusCode": "500",
                    },
                ]
            )

        second_sql_requirement = api.root.add_resource("second_sql_requirement")
        second_sql_requirement.add_method(
            "GET",
            operation_name="ListOfEmployeesReport",
            integration=second_sql_requirement_integration,
            method_responses=[
                {
                    "statusCode": "200",
                },
                {
                    "statusCode": "400",
                },
                {
                    "statusCode": "500",
                },
            ],
        )

        # =============== Permissions ===============

        db_secret = sm.Secret.from_secret_name_v2(
            self, "DBCredentialsSecret", lambda_config.get("secret_name")
        )

        db_secret.grant_read(db_migration_fun)
        db_secret.grant_read(first_sql_fun)
        db_secret.grant_read(second_sql_fun)
 