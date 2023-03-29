#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import sys

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template


@pytest.fixture(scope="function")
def stack_defaults():
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
    os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
    os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"
    os.environ["SEEDFARMER_HASH"] = "xxxxxxxx"
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"
    os.environ["SEEDFARMER_PARAMETER_ENCRYPTION_TYPE"] = "SSE"
    os.environ["SEEDFARMER_PARAMETER_RETENTION_TYPE"] = "DESTROY"

    # Unload the app import so that subsequent tests don't reuse
    if "app" in sys.modules:
        del sys.modules["app"]
    if "stack" in sys.modules:
        del sys.modules["stack"]


def test_synthesize_stack(stack_defaults):
    import stack

    app = cdk.App()
    project_name = os.environ["SEEDFARMER_PROJECT_NAME"]
    dep_name = os.environ["SEEDFARMER_DEPLOYMENT_NAME"]
    mod_name = os.environ["SEEDFARMER_MODULE_NAME"]
    # Create the Stack.
    bucket_stack = stack.BucketsStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=os.environ["SEEDFARMER_PROJECT_NAME"],
        deployment_name=os.environ["SEEDFARMER_DEPLOYMENT_NAME"],
        module_name=os.environ["SEEDFARMER_MODULE_NAME"],
        buckets_encryption_type=os.environ["SEEDFARMER_PARAMETER_ENCRYPTION_TYPE"],
        buckets_retention=os.environ["SEEDFARMER_PARAMETER_RETENTION_TYPE"],
        hash=os.environ["SEEDFARMER_HASH"],
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(bucket_stack)

    template.resource_count_is("AWS::S3::Bucket", 2)
    template.resource_count_is("AWS::S3::BucketPolicy", 2)
