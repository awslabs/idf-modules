# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import os
from typing import Callable, TypeVar

from aws_cdk import App, CfnOutput, Environment

from stack import TemplateStack

# Project specific
project_name: str = os.getenv("SEEDFARMER_PROJECT_NAME")
deployment_name: str = os.getenv("SEEDFARMER_DEPLOYMENT_NAME")
module_name: str = os.getenv("SEEDFARMER_MODULE_NAME")

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")


T = TypeVar("T")
EnvFunction = Callable[[str], T]


def _get_env(
    name: str, required: bool = False, default_value: T | None = None, function: EnvFunction | None = None
) -> T | str | None:
    env_value = os.getenv(f"SEEDFARMER_PARAMETER_{name}")

    if env_value is None and required:
        raise ValueError(f"Missing required environment variable SEEDFARMER_PARAMETER_{name}")

    if env_value is None and not required:
        return default_value

    if function is None:
        return env_value

    return function(env_value)


vpc_id: str = _get_env("VPC_ID", required=True)
private_subnet_ids: list[str] = _get_env("PRIVATE_SUBNET_IDS", required=True, function=json.loads)

engine: str = _get_env("ENGINE", required=True)
username: str = _get_env("ADMIN_USERNAME", required=True)
port: int | None = _get_env("PORT", required=False, function=int)
db_retention: str = _get_env("DB_RETENTION", required=False, default_value="RETAIN", function=str.upper)
instance_type: str = _get_env("INSTANCE_TYPE", required=False, default_value="t2.small")
multi_az: bool = _get_env("MULTI_AZ", required=False, default_value=False, function=lambda x: x.lower() == "true")


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


app = App()

template_stack = TemplateStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    stack_description=generate_description(),
    env=Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
    vpc_id=vpc_id,
    private_subnet_ids=private_subnet_ids,
    engine=engine,
    username=username,
    port=port,
    db_retention=db_retention,
    instance_type=instance_type,
    multi_az=multi_az,
)


CfnOutput(
    scope=template_stack,
    id="metadata",
    value=template_stack.to_json_string(
        {
            "CredentialsSecretArn": template_stack.db_credentials_secret.secret_arn,
            "DatabaseHostname": template_stack.database.instance_endpoint.hostname,
            "DatabasePort": template_stack.database.instance_endpoint.port,
        }
    ),
)

app.synth()
