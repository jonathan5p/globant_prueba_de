from aws_cdk import (
    Stack,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_kms as kms,
    aws_iam as iam,
)
from constructs import Construct


class RdsStack(Stack):
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

    def main(self) -> None:

        # ===============  Storage KMS Key  ===============

        kms_db_key = kms.Key(
            self,
            "DbKey",
            alias=self.app_prefix + "db-encryption-key",
            description="Test database kms encryption key",
            enabled=True,
            enable_key_rotation=True,
        )

        # =============== KMS Key Policy ===============

        encryptDecryptPolicy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                # DECRYPT_ACTIONS
                "kms:Decrypt",
                # ENCRYPT_ACTIONS
                "kms:Encrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
            ],
        )

        encryptDecryptPolicy.add_service_principal("rds.amazonaws.com")
        kms_db_key.add_to_resource_policy(encryptDecryptPolicy)

        # ===============  Aurora test db  ===============

        # Generate cluster admin credentials (Stored in secrets manager)
        self.cluster_secret = rds.DatabaseSecret(
            self,
            self.app_prefix + "AuroraDBClusterSecret",
            username="dbadmin",
            secret_name=self.app_prefix + "AuroraDBClusterSecret",
        )

        cluster_credentials = rds.Credentials.from_secret(secret=self.cluster_secret)
        db_engine = rds.DatabaseClusterEngine.aurora_mysql(
            version=rds.AuroraMysqlEngineVersion.VER_3_02_0
        )

        self.cluster = rds.DatabaseCluster(
            self,
            self.app_prefix + "MysqlDatabase",
            cluster_identifier=self.app_prefix + "MysqlDatabase",
            engine=db_engine,
            credentials=cluster_credentials,
            default_database_name="test_db",
            storage_encryption_key=kms_db_key,
            # Cluster instance configuration ñ{
            # (all instances in the cluster are deployed using this settings)
            instance_props=rds.InstanceProps(
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MEDIUM
                ),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                ),
                vpc=self.networking_stack.project_vpc,
                security_groups=[self.networking_stack.auroradb_sg],
            ),
        )

        # ===============  Bastion Instance  ===============

        # Creation of a bastion instance for test purposes
        bastion = ec2.BastionHostLinux(
            self,
            self.app_prefix + "BastionHost",
            instance_name=self.app_prefix + "BastionHost",
            vpc=self.networking_stack.project_vpc,
            security_group=self.networking_stack.lambda_sg,
        )

        # User data used to install mysql in our bastion instance
        bastion.instance.add_user_data("sudo yum install mysql -y")
