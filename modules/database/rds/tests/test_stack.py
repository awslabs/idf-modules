# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import aws_cdk as cdk
import cdk_nag
import pytest
from aws_cdk.assertions import Annotations, Match, Template


@pytest.fixture(scope="function")
def stack_defaults() -> None:
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

    # Unload the app import so that subsequent tests don't reuse

    if "stack" in sys.modules:
        del sys.modules["stack"]


RDS_ENGINE_SETTINGS = {
    "mysql": {
        "engine_version": "8.0.35",
        "instance_type": "t2.small",
    },
    "postgresql": {
        "engine_version": "14.5",
        "instance_type": "m6gd.large",
    },
}


@pytest.fixture(scope="function")
def rds_stack(stack_defaults, rds_engine: str, credential_rotation_days: int) -> cdk.Stack:
    import stack

    app = cdk.App()
    project_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    engine_version = RDS_ENGINE_SETTINGS[rds_engine]["engine_version"]
    instance_type = RDS_ENGINE_SETTINGS[rds_engine]["instance_type"]

    return stack.RDSDatabaseStack(
        scope=app,
        id=f"{project_name}-{dep_name}-{mod_name}",
        project_name=project_name,
        deployment_name=dep_name,
        module_name=mod_name,
        vpc_id="vpc-12345",
        subnet_ids=["subnet-12345", "subnet-67890", "subnet-91011"],
        database_name="testdb",
        engine=rds_engine,
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


@pytest.mark.parametrize("rds_engine", ["mysql", "postgresql"])
@pytest.mark.parametrize(
    "credential_rotation_days",
    [pytest.param(45, id="credential_rotation"), pytest.param(0, id="no_credential_rotation")],
)
def test_synthesize_stack(rds_stack: cdk.Stack, rds_engine: str, credential_rotation_days: int) -> None:
    template = Template.from_stack(rds_stack)

    template.resource_count_is("AWS::RDS::DBInstance", 1)
    template.has_resource_properties(
        "AWS::RDS::DBInstance",
        {
            "Engine": "postgres" if rds_engine == "postgresql" else rds_engine,
            "DBInstanceClass": f"db.{RDS_ENGINE_SETTINGS[rds_engine]['instance_type']}",
        },
    )

    if credential_rotation_days:
        template.resource_count_is("AWS::SecretsManager::RotationSchedule", 1)
        template.has_resource_properties(
            "AWS::SecretsManager::RotationSchedule",
            {
                "RotationRules": {
                    "ScheduleExpression": f"rate({credential_rotation_days} days)",
                }
            },
        )
    else:
        template.resource_count_is("AWS::SecretsManager::RotationSchedule", 0)


@pytest.mark.parametrize("rds_engine", ["mysql", "postgresql"])
@pytest.mark.parametrize(
    "credential_rotation_days",
    [pytest.param(45, id="credential_rotation"), pytest.param(0, id="no_credential_rotation")],
)
def test_no_cdk_nag_errors(rds_stack: cdk.Stack, rds_engine: str, credential_rotation_days: int) -> None:
    cdk.Aspects.of(rds_stack).add(cdk_nag.AwsSolutionsChecks())

    nag_errors = Annotations.from_stack(rds_stack).find_error(
        "*",
        Match.string_like_regexp(r"AwsSolutions-.*"),
    )
    assert not nag_errors, f"Found {len(nag_errors)} CDK nag errors"
