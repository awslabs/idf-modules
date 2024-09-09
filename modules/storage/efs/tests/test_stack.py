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
    from stack import EFSFileStorage

    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    return EFSFileStorage(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        vpc_id="vpc-12345",
        efs_removal_policy="DESTROY",
        env=cdk.Environment(
            account="111111111111",
            region="us-east-1",
        ),
    )


def test_synthesize_stack(stack: cdk.Stack) -> None:
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::EFS::FileSystem", 1)


def test_no_cdk_nag_errors(stack: cdk.Stack) -> None:
    cdk.Aspects.of(stack).add(cdk_nag.AwsSolutionsChecks())

    nag_errors = Annotations.from_stack(stack).find_error(
        "*",
        Match.string_like_regexp(r"AwsSolutions-.*"),
    )
    assert not nag_errors, f"Found {len(nag_errors)} CDK nag errors"
