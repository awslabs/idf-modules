# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os

import aws_cdk
from aws_cdk import App, CfnOutput

from stack import NeptuneStack

# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")

if len(f"{project_name}-{deployment_name}") > 36:
    raise Exception("This module cannot support a project+deployment name character length greater than 35")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


# App specific
vpc_id = os.getenv(_param("VPC_ID"))  # required
private_subnet_ids = json.loads(os.getenv(_param("PRIVATE_SUBNET_IDS"), ""))  # required

if not vpc_id:
    raise Exception("missing input parameter vpc-id")

if not private_subnet_ids:
    raise Exception("missing input parameter private-subnet-ids")

num_instances = int(os.getenv(_param("NUMBER_INSTANCES"), "1"))

app = App()

stack = NeptuneStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
    deployment_name=deployment_name,
    module_name=module_name,
    vpc_id=vpc_id,
    private_subnet_ids=private_subnet_ids,
    number_instances=num_instances,
)

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "NeptuneClusterId": stack.cluster.cluster_identifier,
            "NeptuneEndpointAddress": stack.cluster.cluster_endpoint.socket_address,
            "NeptuneReadEndpointAddress": stack.cluster.cluster_read_endpoint.socket_address,
            "NeptuneSecurityGroupId": stack.sg_graph_db.security_group_id,
        }
    ),
)


app.synth(force=True)
