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
    from stack import BucketsStack

    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    return BucketsStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        partition="aws",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        buckets_encryption_type="SSE",
        buckets_retention="DESTROY",
        hash="xxxxxxxx",
        stack_description="Testing",
        env=cdk.Environment(
            account="111111111111",
            region="us-east-1",
        ),
    )


def test_synthesize_stack(stack: cdk.Stack) -> None:
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::S3::Bucket", 2)
    template.resource_count_is("AWS::S3::BucketPolicy", 2)


def test_bucket_hash() -> None:
    import stack

    assert (
        len(
            stack.bucket_hash(
                bucket_name="bucket-name-over-max-123456789123456789123456789123456789123456789123456789",
                module_name="unit-tests",
            )
        )
        <= 63
    )

    assert stack.bucket_hash(bucket_name="my-bucket", module_name="foobar").startswith("my-bucket-")


def test_no_cdk_nag_errors(stack: cdk.Stack) -> None:
    cdk.Aspects.of(stack).add(cdk_nag.AwsSolutionsChecks())

    nag_errors = Annotations.from_stack(stack).find_error(
        "*",
        Match.string_like_regexp(r"AwsSolutions-.*"),
    )
    assert not nag_errors, f"Found {len(nag_errors)} CDK nag errors"
