import json
import os
import sys
from typing import Dict, List

import aws_cdk as cdk
import boto3
from aws_cdk import cloud_assembly_schema as cas
from aws_cdk import integ_tests_alpha as integration

sys.path.append("../")

import stack  # noqa: E402

app = cdk.App()


def get_module_dependencies(resource_keys: List[str]) -> Dict[str, str]:
    ssm = boto3.client("ssm", region_name="us-east-1")
    dependencies = {}
    try:
        for key in resource_keys:
            dependencies[key] = ssm.get_parameter(Name=f"/module-integration-tests/{key}")["Parameter"]["Value"]
    except Exception as e:
        print(f"issue getting dependencies: {e}")
    return dependencies


dependencies = get_module_dependencies(
    # Add any required resource identifiers here
    resource_keys=["vpc-id", "vpc-private-subnets"]
)

rds_stack = stack.RDSDatabaseStack(
    app,
    "rds-integ-stack",
    project_name="test-project",
    deployment_name="test-deployment",
    module_name="test-module",
    vpc_id=dependencies["vpc-id"],
    subnet_ids=json.loads(dependencies["vpc-private-subnets"]),
    engine="mysql",
    engine_version="8.0.35",
    database_name="testdb",
    username="admin",
    credential_rotation_days=30,
    instance_type="t3.small",
    is_accessible_from_vpc=True,
    removal_policy=cdk.RemovalPolicy.DESTROY,
    env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region="us-east-1"),
)

integration.IntegTest(
    app,
    "Integration Tests RDS Database Module",
    test_cases=[
        rds_stack,
    ],
    diff_assets=True,
    stack_update_workflow=True,
    enable_lookups=True,
    regions=["us-east-1"],
    cdk_command_options=cas.CdkCommands(
        deploy=cas.DeployCommand(args=cas.DeployOptions(require_approval=cas.RequireApproval.NEVER, json=True)),
        destroy=cas.DestroyCommand(args=cas.DestroyOptions(force=True)),
    ),
)

app.synth()
