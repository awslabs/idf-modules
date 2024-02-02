# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os

import aws_cdk
from aws_cdk import App, CfnOutput

from stacks.oss_stack import OpenSearchServerlessStack
from stacks.oss_vpce_stack import OpenSearchServerlessVpcEndpointStack


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")
hash = os.getenv("SEEDFARMER_HASH", "")

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")

# App specific

vpc_id = os.getenv(_param("VPC_ID"))
private_subnet_ids = json.loads(os.getenv(_param("PRIVATE_SUBNET_IDS")))  # type: ignore

if not vpc_id:
    raise ValueError("missing input parameter vpc-id")

if not private_subnet_ids:
    raise ValueError("missing input parameter private-subnet-ids")

# REF: developerguide/supported-instance-types.html

ENV = aws_cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"],
)

app = App()

oss_vpce_stack = OpenSearchServerlessVpcEndpointStack(
    app,
    id=f"{project_name}-{deployment_name}-{module_name}-OSSVpce",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    vpc_id=vpc_id,
    private_subnet_ids=private_subnet_ids,
    env=ENV,
)

oss_stack = OpenSearchServerlessStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    hash=hash,
    vpc_id=vpc_id,
    private_subnet_ids=private_subnet_ids,
    vpc_endpoint_id=oss_vpce_stack.vpc_endpoint_id,
    oss_cluster_sg_id=oss_vpce_stack.oss_cluster_sg_id,
    env=ENV,
)
oss_stack.add_dependency(oss_vpce_stack)

CfnOutput(
    scope=oss_stack,
    id="metadata",
    value=oss_stack.to_json_string(
        {
            "OpenSearchCollectionEndpoint": oss_stack.cfn_collection.attr_collection_endpoint,
            "OpenSearchDashboardEndpoint": oss_stack.cfn_collection.attr_dashboard_endpoint,
            "OpenSearchCollectionSecurityGroupId": oss_stack.oss_cluster_sg_id,
        }
    ),
)

app.synth(force=True)
