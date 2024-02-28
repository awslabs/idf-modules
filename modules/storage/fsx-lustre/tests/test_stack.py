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

    fsx_stack = stack.FsxFileSystem(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        vpc_id="vpc-12345",
        fs_deployment_type="PERSISTENT_2",
        private_subnet_ids=["subnet-1234", "subnet-5678"],
        storage_throughput=50,
        data_bucket_name="mybucket",
        export_path=None,
        import_path=None,
        stack_description="Tesing",
        file_system_type_version="2.15",
        import_policy="NEW",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(fsx_stack)
    template.resource_count_is("AWS::EC2::SecurityGroup", 1)
    template.resource_count_is("AWS::FSx::FileSystem", 1)
