#!/usr/bin/env python3
import os
import yaml
import aws_cdk as cdk
from globant_prueba.cicd_pipeline import GlobantAPICicdPipelineStack

app = cdk.App()

with open("./config-files/configs.yaml") as file:
    config_yaml = yaml.load(file, Loader=yaml.FullLoader)

env_config = config_yaml.get("Environment")
config_tags = config_yaml.get("Tags")
stack_config = config_yaml.get("Stacks")

# Add tags to all resources within the stackclear
if len(config_tags) > 0:
    for tag, value in config_tags.items():
        cdk.Tags.of(app).add(tag, value)

# Environment prefix
app_prefix = (
    env_config.get("ProjectName") + "-" + env_config.get("Name") + "-"
).lower()

GlobantAPICicdPipelineStack(
    app,
    "GlobantAPICicdPipelineStack",
    env=cdk.Environment(
        account=env_config.get("Account"), region=env_config.get("Region")
    ),
    description="CICD API Pipeline",
    env_config=env_config,
    stack_config=stack_config,
    app_prefix=app_prefix
)


app.synth()
