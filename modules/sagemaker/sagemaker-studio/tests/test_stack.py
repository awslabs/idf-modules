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
    studio_domain_name = "test-domain"
    studio_bucket_name = "test-bucket"
    data_science_users = ["ds-user-1"]
    lead_data_science_users = ["lead-ds-user-1"]
    app_image_config_name = None
    image_name = None
    enable_custom_sagemaker_projects = False

    stack = stack.SagemakerStudioStack(
        app,
        f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        vpc_id="vpc-12345",
        subnet_ids=["subnet-12345", "subnet-54321"],
        studio_domain_name=studio_domain_name,
        studio_bucket_name=studio_bucket_name,
        data_science_users=data_science_users,
        lead_data_science_users=lead_data_science_users,
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
        app_image_config_name=app_image_config_name,
        image_name=image_name,
        enable_custom_sagemaker_projects=enable_custom_sagemaker_projects,
    )

    template = Template.from_stack(stack)

    template.resource_count_is("AWS::SageMaker::Domain", 1)
