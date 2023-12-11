# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import aws_cdk as cdk
from aws_cdk import CfnOutput

from stack import CustomKernelStack

project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")
app_prefix = f"{project_name}-{deployment_name}-{module_name}"

DEFAULT_APP_IMAGE_CONFIG_NAME = f"{project_name}-{deployment_name}-app-config"


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


sagemaker_image_name = os.getenv(_param("SAGEMAKER_IMAGE_NAME"))
app_image_config_name = os.getenv(_param("APP_IMAGE_CONFIG_NAME"), DEFAULT_APP_IMAGE_CONFIG_NAME)


environment = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"],
)

app = cdk.App()
stack = CustomKernelStack(
    scope=app,
    construct_id=app_prefix,
    app_prefix=app_prefix,
    env=environment,
)

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "SageMakerCustomKernelRoleArn": stack.sagemaker_studio_image_role.role_arn,
        }
    ),
)

app.synth()
