Implemented architecture for the Globant Data Enginneer interview test.

[Arquitecture Diagram](./images/GlobantArq.pdf)

# Prerequisites!

For CDK and permissions:

* CDK Version 2

* Create a CDK deployment role (you can also use the one created by cdk when doing bootstrapping, but it is recomended to create a custom role just for CDK usage)
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

* NetworkingStack
* RdsStack
* GlobantPruebaStack