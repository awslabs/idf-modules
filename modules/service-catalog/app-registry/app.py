# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from aws_cdk import App, CfnOutput, Environment

from stack import AppRegistry

# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")


if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


# App specific
solution_id = os.getenv(_param("SOLUTION_ID"))  # required
solution_name = os.getenv(_param("SOLUTION_NAME"))  # required
solution_version = os.getenv(_param("SOLUTION_VERSION"))  # required


if not solution_id:
    raise ValueError("Missing input parameter solution-id")

if not solution_name:
    raise ValueError("Missing input parameter solution-name")

if not solution_version:
    raise ValueError("Missing input parameter solution-version")


app = App()

stack = AppRegistry(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    solution_id=solution_id,
    solution_name=solution_name,
    solution_version=solution_version,
    env=Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "AppRegistryName": stack.app_registry.name,
            "AttributeGroupName": stack.attribute_group.name,
        }
    ),
)

app.synth(force=True)
