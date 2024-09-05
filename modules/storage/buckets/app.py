# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import aws_cdk
import cdk_nag

from stack import BucketsStack

project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")
hash = os.getenv("SEEDFARMER_HASH", "")
partition = os.getenv("AWS_PARTITION", "aws")

buckets_encryption_type = os.getenv("SEEDFARMER_PARAMETER_ENCRYPTION_TYPE", "SSE")
buckets_retention = os.getenv("SEEDFARMER_PARAMETER_RETENTION_TYPE", "RETAIN")


app = aws_cdk.App()

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")

if buckets_retention not in ["DESTROY", "RETAIN"]:
    raise ValueError("The only RETENTION_TYPE values accepted are 'DESTROY' and 'RETAIN' ")


if buckets_encryption_type not in ["SSE", "KMS"]:
    raise ValueError("The only ENCRYPTION_TYPE values accepted are 'SSE' and 'KMS' ")


def generate_description() -> str:
    soln_id = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_ID", None)
    soln_name = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_NAME", None)
    soln_version = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_VERSION", None)

    desc = "IDF - Buckets Module"
    if soln_id and soln_name and soln_version:
        desc = f"({soln_id}) {soln_name}. Version {soln_version}"
    elif soln_id and soln_name:
        desc = f"({soln_id}) {soln_name}"
    return desc


stack = BucketsStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    partition=partition,
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    buckets_encryption_type=buckets_encryption_type,
    buckets_retention=buckets_retention,
    hash=hash,
    stack_description=generate_description(),
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

aws_cdk.CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "ArtifactsBucketName": stack.artifacts_bucket.bucket_name,
            "LogsBucketName": stack.logs_bucket.bucket_name,
            "ReadOnlyPolicyArn": stack.readonly_policy.managed_policy_arn,
            "FullAccessPolicyArn": stack.fullaccess_policy.managed_policy_arn,
        }
    ),
)

aws_cdk.Aspects.of(app).add(cdk_nag.AwsSolutionsChecks(log_ignores=True))

app.synth(force=True)
