# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os

import aws_cdk
from aws_cdk import App, CfnOutput

from stack import NetworkingStack

project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


vpc_cidr = os.getenv(_param("VPC_CIDR"), "10.0.0.0/16")
cidr_mask = int(os.getenv(_param("CIDR_MASK"), "24"))
internet_accessible = json.loads(os.getenv(_param("INTERNET_ACCESSIBLE"), "true"))
local_zones = json.loads(os.getenv(_param("LOCAL_ZONES"), "[]"))

app = App()


def generate_description() -> str:
    soln_id = os.getenv(_param("SOLUTION_ID"), None)
    soln_name = os.getenv(_param("SOLUTION_NAME"), None)
    soln_version = os.getenv(_param("SOLUTION_VERSION"), None)

    desc = f"{project_name} - Networking Module"
    if soln_id and soln_name and soln_version:
        desc = f"({soln_id}) {soln_name}. Version {soln_version}"
    elif soln_id and soln_name:
        desc = f"({soln_id}) {soln_name}"
    return desc


stack = NetworkingStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    vpc_cidr=vpc_cidr,
    cidr_mask=cidr_mask,
    internet_accessible=internet_accessible,
    local_zones=local_zones,
    stack_description=generate_description(),
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "VpcId": stack.vpc.vpc_id,
            "SecurityGroupId": stack._vpc_security_group.security_group_id,
            "PublicSubnetIds": stack.public_subnets.subnet_ids,
            "PrivateSubnetIds": stack.private_subnets.subnet_ids,
            "IsolatedSubnetIds": stack.isolated_subnets.subnet_ids if not stack.internet_accessible else [],
            "LocalZonePrivateSubnetIds": [s.subnet_id for s in stack.local_zone_private_subnets if local_zones]
            if hasattr(stack, "local_zone_private_subnets") and local_zones
            else [],
            "LocalZonePublicSubnetIds": [s.subnet_id for s in stack.local_zone_public_subnets if local_zones]
            if hasattr(stack, "local_zone_public_subnets") and local_zones
            else [],
        }
    ),
)

app.synth(force=True)
