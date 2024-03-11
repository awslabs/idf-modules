# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import os

import aws_cdk as cdk
import cdk_nag

from stack import RDSDatabaseStack

# Project specific
project_name: str = os.environ["SEEDFARMER_PROJECT_NAME"]
deployment_name: str = os.environ["SEEDFARMER_DEPLOYMENT_NAME"]
module_name: str = os.environ["SEEDFARMER_MODULE_NAME"]

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


def _get_env(name: str, default: str | None = None, required: bool = True) -> str | None:
    param_name = _param(name)
    value = os.getenv(param_name, default)

    if required and not value:
        raise ValueError(f"Missing input parameter {param_name}")

    return value


vpc_id: str = _get_env("VPC_ID")  # type: ignore[assignment]
subnet_ids: list[str] = json.loads(_get_env("SUBNET_IDS", required=True))  # type: ignore[arg-type,assignment]
engine: str = _get_env("ENGINE", required=True)  # type: ignore[assignment]
engine_version: str = _get_env("ENGINE_VERSION", required=True)  # type: ignore[assignment]
username: str = _get_env("ADMIN_USERNAME", required=True)  # type: ignore[assignment]
database_name: str = _get_env("DATABASE_NAME", required=True)  # type: ignore[assignment]

port: str | None = _get_env("PORT", required=False)
instance_type: str = _get_env("INSTANCE_TYPE", required=False, default="t2.small")  # type: ignore[assignment]
credential_rotation_days: int = int(
    _get_env("CREDENTIAL_ROTATION_DAYS", required=False, default="0"),  # type: ignore[arg-type]
)
is_accessible_from_vpc = json.loads(
    _get_env("ACCESSIBLE_FROM_VPC", required=False, default="false"),  # type: ignore[arg-type]
)


def _parse_removal_policy(value: str) -> cdk.RemovalPolicy:
    value = value.upper()

    if value == "DESTROY":
        return cdk.RemovalPolicy.DESTROY
    if value == "RETAIN":
        return cdk.RemovalPolicy.RETAIN

    raise ValueError(f"Invalid removal policy {value}")


removal_policy: cdk.RemovalPolicy = _parse_removal_policy(
    _get_env(  # type: ignore[arg-type]
        "REMOVAL_POLICY",
        required=False,
        default="retain",
    )
)


def generate_description() -> str:
    soln_id = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_ID", None)
    soln_name = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_NAME", None)
    soln_version = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_VERSION", None)

    desc = "My Module Default Description"
    if soln_id and soln_name and soln_version:
        desc = f"({soln_id}) {soln_name}. Version {soln_version}"
    elif soln_id and soln_name:
        desc = f"({soln_id}) {soln_name}"
    return desc


app = cdk.App()

template_stack = RDSDatabaseStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    stack_description=generate_description(),
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
    vpc_id=vpc_id,
    subnet_ids=subnet_ids,
    database_name=database_name,
    engine=engine,
    engine_version=engine_version,
    username=username,
    credential_rotation_days=credential_rotation_days,
    is_accessible_from_vpc=is_accessible_from_vpc,
    port=int(port) if port else None,
    removal_policy=removal_policy,
    instance_type=instance_type,
)


cdk.CfnOutput(
    scope=template_stack,
    id="metadata",
    value=template_stack.to_json_string(
        {
            "CredentialsSecretArn": template_stack.db_credentials_secret.secret_arn,
            "DatabaseHostname": template_stack.database.instance_endpoint.hostname,
            "DatabasePort": template_stack.database.instance_endpoint.port,
            "SecurityGroupId": template_stack.sg_rds.security_group_id,
        }
    ),
)

cdk.Aspects.of(template_stack).add(cdk_nag.AwsSolutionsChecks(log_ignores=True))

app.synth()
