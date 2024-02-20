# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template


@pytest.fixture(scope="function", autouse=True)
def stack_defaults() -> None:
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

    # Unload the app import so that subsequent tests don't reuse

    if "stack" in sys.modules:
        del sys.modules["stack"]


@pytest.fixture(scope="session")
def rds_configuration(request: pytest.FixtureRequest) -> dict[str, str]:
    engine: str = request.param  # type: ignore

    engine_config_map = {
        "mysql": {
            "engine": "mysql",
            "engine_version": "8.0.35",
            "instance_type": "t2.small",
        },
        "postgresql": {
            "engine": "postgresql",
            "engine_version": "14.5",
            "instance_type": "m6gd.large",
        },
    }

    return engine_config_map[engine]


@pytest.mark.parametrize("rds_configuration", ["mysql", "postgresql"], indirect=True)
def test_synthesize_stack(rds_configuration: dict[str, str]) -> None:
    import stack

    app = cdk.App()
    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    engine = rds_configuration["engine"]
    engine_version = rds_configuration["engine_version"]
    instance_type = rds_configuration["instance_type"]
    credential_rotation_days = 45

    rds_stack = stack.RDSDatabaseStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        vpc_id="vpc-12345",
        subnet_ids=["subnet-12345", "subnet-67890", "subnet-91011"],
        engine=engine,
        engine_version=engine_version,
        username="admin",
        credential_rotation_days=credential_rotation_days,
        instance_type=instance_type,
        removal_policy=cdk.RemovalPolicy.DESTROY,
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(rds_stack)

    template.resource_count_is("AWS::RDS::DBInstance", 1)
    template.has_resource_properties(
        "AWS::RDS::DBInstance",
        {
            "Engine": "postgres" if engine == "postgresql" else engine,
            "DBInstanceClass": f"db.{instance_type}",
        },
    )

    template.resource_count_is("AWS::SecretsManager::RotationSchedule", 1)
    template.has_resource_properties(
        "AWS::SecretsManager::RotationSchedule",
        {
            "RotationRules": {
                "ScheduleExpression": f"rate({credential_rotation_days} days)",
            }
        },
    )


@pytest.mark.parametrize("rds_configuration", ["mysql", "postgresql"], indirect=True)
def test_synthesize_stack_no_credential_rotation(rds_configuration: dict[str, str]) -> None:
    import stack

    app = cdk.App()
    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    engine = rds_configuration["engine"]
    engine_version = rds_configuration["engine_version"]
    instance_type = rds_configuration["instance_type"]

    rds_stack = stack.RDSDatabaseStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        vpc_id="vpc-12345",
        subnet_ids=["subnet-12345", "subnet-67890", "subnet-91011"],
        engine=engine,
        engine_version=engine_version,
        username="admin",
        credential_rotation_days=0,
        instance_type=instance_type,
        removal_policy=cdk.RemovalPolicy.DESTROY,
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(rds_stack)

    template.resource_count_is("AWS::SecretsManager::RotationSchedule", 0)
