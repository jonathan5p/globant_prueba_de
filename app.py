#!/usr/bin/env python3
import os
import yaml
import aws_cdk as cdk
from globant_prueba.globant_prueba_stack import GlobantPruebaStack
from globant_prueba.networking_stack import NetworkingStack
from globant_prueba.rds_test_stack import RdsStack

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


networking_stack = NetworkingStack(
    app,
    "NetworkingStack",
    env=cdk.Environment(
        account=env_config.get("Account"), region=env_config.get("Region")
    ),
    description="Networking resources",
    env_config=env_config,
    stack_config=stack_config.get("NetworkingStack") if stack_config != None else None,
    app_prefix=app_prefix,
)

rds_stack = RdsStack(
    app,
    "RdsStack",
    env=cdk.Environment(
        account=env_config.get("Account"), region=env_config.get("Region")
    ),
    description="Tes MySql DB resources",
    env_config=env_config,
    stack_config=stack_config.get("RdsStack") if stack_config != None else None,
    app_prefix=app_prefix,
    networking_stack=networking_stack
).add_dependency(networking_stack)

api_stack = GlobantPruebaStack(
    app,
    "GlobantPruebaStack",
    env=cdk.Environment(
        account=env_config.get("Account"), region=env_config.get("Region")
    ),
    description="API resources",
    env_config=env_config,
    stack_config=stack_config.get("GlobantPruebaStack") if stack_config != None else None,
    app_prefix=app_prefix,
    networking_stack=networking_stack
).add_dependency(networking_stack)

app.synth()
