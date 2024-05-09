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

    bucket_stack = stack.BucketsStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        buckets_encryption_type="SSE",
        buckets_retention="DESTROY",
        hash="xxxxxxxx",
        stack_description="Testing",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(bucket_stack)

    template.resource_count_is("AWS::S3::Bucket", 2)
    template.resource_count_is("AWS::S3::BucketPolicy", 2)


def test_bucket_hash():
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
