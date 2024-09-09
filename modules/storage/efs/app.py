# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import aws_cdk
import cdk_nag
from aws_cdk import App, Aspects, CfnOutput

from stack import EFSFileStorage

# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")

# App specific
vpc_id = os.getenv("SEEDFARMER_PARAMETER_VPC_ID")

efs_removal_policy = os.getenv("SEEDFARMER_PARAMETER_RETENTION_TYPE", "DESTROY")

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")

if not vpc_id:
    raise ValueError("missing input parameter vpc-id")

if efs_removal_policy not in ["DESTROY", "RETAIN"]:
    raise ValueError("The only RETENTION_TYPE values accepted are 'DESTROY' and 'RETAIN' ")

app = App()


efs_stack = EFSFileStorage(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    vpc_id=vpc_id,
    efs_removal_policy=efs_removal_policy,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)
CfnOutput(
    scope=efs_stack,
    id="metadata",
    value=efs_stack.to_json_string(
        {
            "EFSFileSystemId": efs_stack.efs_filesystem.file_system_id,
            "EFSFileSystemArn": efs_stack.efs_filesystem.file_system_arn,
            "EFSSecurityGroupId": efs_stack.efs_security_group.security_group_id,
            "VPCId": efs_stack.vpc_id,
        }
    ),
)

Aspects.of(app).add(cdk_nag.AwsSolutionsChecks(log_ignores=True))

app.synth(force=True)
