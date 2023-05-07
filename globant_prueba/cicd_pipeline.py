from aws_cdk import Stack
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from aws_cdk.aws_codepipeline_actions import GitHubTrigger
from globant_prueba.cicd_stages.globant_prueba_stack_stage import GlobantPruebaStage


class GlobantAPICicdPipelineStack(Stack):
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

        repository = CodePipelineSource.git_hub(
            "jonathan5p/globant_prueba_de",
            "main",
            authentication=cdk.SecretValue.secrets_manager("github-token"),
            trigger=GitHubTrigger.WEBHOOK
        )

        self.pipeline = CodePipeline(
            self,
            "Pipeline",
            pipeline_name="GlobantAPIPipeline",
            synth=ShellStep(
                "Synth",
                input=repository,
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth",
                ],
            ),
            cross_account_keys=True,
        )

        stage = GlobantPruebaStage(
            self,
            "GlobantPruebaStack",
            env=cdk.Environment(
                account=self.env_config.get("Account"),
                region=self.env_config.get("Region"),
            ),
            env_config=self.env_config,
            stack_config=self.stack_config,
            app_prefix=self.app_prefix,
        )

        self.pipeline.add_stage(stage)
