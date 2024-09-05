# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import aws_cdk as cdk
import cdk_nag
import pytest
from aws_cdk.assertions import Annotations, Match, Template


@pytest.fixture(scope="function")
def app() -> cdk.App:
    return cdk.App()


@pytest.fixture(scope="function")
def stack(app: cdk.App) -> cdk.Stack:
    from stack import OpenSearchStack

    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    return OpenSearchStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        hash="abcdefgh",
        os_domain_retention="DESTROY",
        vpc_id="vpc-12345",
        private_subnet_ids=["subnet-12345", "subnet-54321"],
        os_data_nodes=1,
        os_data_node_instance_type="r6g.large.search",
        os_master_nodes=0,
        os_master_node_instance_type="r6g.large.search",
        os_ebs_volume_size=10,
        stack_description="Testing",
        env=cdk.Environment(
            account="111111111111",
            region="us-east-1",
        ),
    )


def test_synthesize_stack(stack: cdk.Stack) -> None:
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::OpenSearchService::Domain", 1)

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
                            "Service": "lambda.amazonaws.com",
                        },
                    },
                ],
            },
        },
    )


def test_no_cdk_nag_errors(stack: cdk.Stack) -> None:
    cdk.Aspects.of(stack).add(cdk_nag.AwsSolutionsChecks())

    nag_errors = Annotations.from_stack(stack).find_error(
        "*",
        Match.string_like_regexp(r"AwsSolutions-.*"),
    )
    assert not nag_errors, f"Found {len(nag_errors)} CDK nag errors"
