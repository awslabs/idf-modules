# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

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
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(bucket_stack)

    template.resource_count_is("AWS::S3::Bucket", 2)
    template.resource_count_is("AWS::S3::BucketPolicy", 2)
