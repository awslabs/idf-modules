# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import aws_cdk as cdk
from aws_cdk import CfnOutput

from stack import EcrStack

project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")
app_prefix = f"{project_name}-{deployment_name}-{module_name}"

DEFAULT_REPOSITORY_NAME = f"{app_prefix}-ecr"
DEFAULT_IMAGE_MUTABILITY = "IMMUTABLE"
DEFAULT_LIFECYCLE = None  # No lifecycle policy
DEFAULT_REMOVAL_POLICY = "DESTROY"


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


environment = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"],
)

repository_name = os.getenv(_param("REPOSITORY_NAME"), DEFAULT_REPOSITORY_NAME)
image_tag_mutability = os.getenv(_param("IMAGE_TAG_MUTABILITY"), DEFAULT_IMAGE_MUTABILITY)
lifecycle_max_image_count = os.getenv(_param("LIFECYCLE_MAX_IMAGE_COUNT"), DEFAULT_LIFECYCLE)
lifecycle_max_days = os.getenv(_param("LIFECYCLE_MAX_DAYS"), DEFAULT_LIFECYCLE)
removal_policy = os.getenv(_param("REMOVAL_POLICY"), DEFAULT_REMOVAL_POLICY)

if removal_policy not in ["DESTROY", "RETAIN"]:
    raise ValueError("The only REMOVAL_POLICY values accepted are 'DESTROY' and 'RETAIN' ")

app = cdk.App()
stack = EcrStack(
    scope=app,
    construct_id=app_prefix,
    repository_name=repository_name,
    image_tag_mutability=image_tag_mutability,
    lifecycle_max_image_count=lifecycle_max_image_count,
    lifecycle_max_days=lifecycle_max_days,
    removal_policy=removal_policy,
    env=environment,
)
metadata = {
    "EcrRepositoryName": stack.repository.repository_name,
    "EcrRepositoryArn": stack.repository.repository_arn,
}

if stack.lifecycle_max_days is not None:
    metadata["LifecycleMaxDays"] = stack.lifecycle_max_days
if stack.lifecycle_max_image_count is not None:
    metadata["LifecycleMaxImages"] = stack.lifecycle_max_image_count

CfnOutput(stack, "metadata", value=stack.to_json_string(metadata))

app.synth()
