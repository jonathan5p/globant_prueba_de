import aws_cdk as cdk
from aws_cdk import Stack
from constructs import Construct
from globant_prueba.cicd_stacks.globant_prueba_stack import GlobantPruebaStack
from globant_prueba.cicd_stacks.networking_stack import NetworkingStack
from globant_prueba.cicd_stacks.rds_test_stack import RdsStack

class GlobantPruebaStage(cdk.Stage):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_config: dict,
        app_prefix: str,
        stack_config: dict,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)
        self.env_config = env_config
        self.stack_config = stack_config
        self.app_prefix = app_prefix
        self.main()

    def main(self):

        networking_stack = NetworkingStack(
            self,
            "NetworkingStack",
            env=cdk.Environment(
                account=self.env_config.get("Account"), region=self.env_config.get("Region")
            ),
            description="Networking resources to test the API",
            env_config=self.env_config,
            stack_config=self.stack_config.get("NetworkingStack") if self.stack_config != None else None,
            app_prefix=self.app_prefix,
        )

        rds_stack = RdsStack(
            self,
            "RdsStack",
            env=cdk.Environment(
                account=self.env_config.get("Account"), region=self.env_config.get("Region")
            ),
            description="Test MySql DB resources",
            env_config=self.env_config,
            stack_config=self.stack_config.get("RdsStack") if self.stack_config != None else None,
            app_prefix=self.app_prefix,
            networking_stack=networking_stack
        ).add_dependency(networking_stack)


        api_stack = GlobantPruebaStack(
            self,
            "GlobantPruebaStack",
            env=cdk.Environment(
                account=self.env_config.get("Account"), region=self.env_config.get("Region")
            ),
            description="API resources",
            env_config=self.env_config,
            stack_config=self.stack_config.get("GlobantPruebaStack") if self.stack_config != None else None,
            app_prefix=self.app_prefix,
            networking_stack=networking_stack
        ).add_dependency(networking_stack)
