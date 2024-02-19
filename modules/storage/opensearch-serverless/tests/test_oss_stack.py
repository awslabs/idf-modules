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
    from stacks.oss_stack import OpenSearchServerlessStack

    app = cdk.App()
    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    oss_stack = OpenSearchServerlessStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        hash="abcdefgh",
        vpc_id="vpc-12345",
        private_subnet_ids=["subnet-12345", "subnet-54321"],
        vpc_endpoint_id="vpce-12345",
        oss_cluster_sg_id="sg-12345",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(oss_stack)

    template.resource_count_is("AWS::OpenSearchServerless::Collection", 1)

    template.resource_count_is("AWS::OpenSearchServerless::SecurityPolicy", 2)

    template.resource_count_is("AWS::OpenSearchServerless::AccessPolicy", 1)

    # Attaches OS access policy...
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "osis-pipelines.amazonaws.com",
                        },
                    },
                ],
            },
        },
    )
