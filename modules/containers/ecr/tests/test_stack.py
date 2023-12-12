# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template


@pytest.fixture(scope="function")
def stack_defaults():
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

    # Unload the app import so that subsequent tests don't reuse

    if "stack" in sys.modules:
        del sys.modules["stack"]


def test_synthesize_stack(stack_defaults):
    import stack

    app = cdk.App()
    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"
    app_prefix = f"{project_name}-{dep_name}-{mod_name}"
    repository_name = "dummy"
    image_tag_mutability = "IMMUTABLE"
    lifecycle = None

    stack = stack.EcrStack(
        scope=app,
        construct_id=app_prefix,
        repository_name=repository_name,
        image_tag_mutability=image_tag_mutability,
        lifecycle_max_image_count=lifecycle,
        lifecycle_max_days=lifecycle,
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(stack)

    template.resource_count_is("AWS::ECR::Repository", 1)
