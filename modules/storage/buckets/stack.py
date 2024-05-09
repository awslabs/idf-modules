# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import hashlib
import logging
from typing import Any, Optional, cast

import aws_cdk
import aws_cdk.aws_iam as aws_iam
import aws_cdk.aws_s3 as aws_s3
import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


def bucket_hash(bucket_name: str, module_name: str, max_length: Optional[int] = 62) -> str:
    if len(bucket_name) > max_length:
        return bucket_name[:max_length]

    return f"""
    {bucket_name}-{hashlib.sha1(module_name.encode('UTF-8'), usedforsecurity=False)
    .hexdigest()[: (max_length-1) - len(bucket_name)]}
    """


class BucketsStack(Stack):  # type: ignore
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        hash: str,
        buckets_encryption_type: str,
        buckets_retention: str,
        stack_description: str,
        **kwargs: Any,
    ) -> None:
        # CDK Env Vars
        account: str = aws_cdk.Aws.ACCOUNT_ID
        region: str = aws_cdk.Aws.REGION

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"
        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod

        super().__init__(scope, id, description=stack_description, **kwargs)
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        artifact_bucket_name = bucket_hash(
            bucket_name=f"{project_name}-{deployment_name}-artifacts-bucket-{hash}",
            module_name=module_name,
        )

        artifacts_bucket = aws_s3.Bucket(
            self,
            id="artifacts-bucket",
            bucket_name=artifact_bucket_name,
            removal_policy=aws_cdk.RemovalPolicy.RETAIN
            if buckets_retention.upper() == "RETAIN"
            else aws_cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=None if buckets_retention.upper() == "RETAIN" else True,
            encryption=aws_s3.BucketEncryption.KMS_MANAGED
            if buckets_encryption_type.upper() == "KMS"
            else aws_s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            event_bridge_enabled=True,
        )

        log_bucket_name = bucket_hash(
            bucket_name=f"{project_name}-{deployment_name}-logs-bucket-{hash}",
            module_name=module_name,
        )

        logs_bucket = aws_s3.Bucket(
            self,
            id="logs-bucket",
            bucket_name=log_bucket_name,
            removal_policy=aws_cdk.RemovalPolicy.RETAIN
            if buckets_retention.upper() == "RETAIN"
            else aws_cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=None if buckets_retention.upper() == "RETAIN" else True,
            encryption=aws_s3.BucketEncryption.KMS_MANAGED
            if buckets_encryption_type.upper() == "KMS"
            else aws_s3.BucketEncryption.S3_MANAGED,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
        )

        # ReadOnly IAM Policy
        readonly_policy = aws_iam.ManagedPolicy(
            self,
            id="readonly_policy",
            managed_policy_name=f"{project_name}-{deployment_name}-{module_name}-{region}-{account}-readonly-access",
            statements=[
                aws_iam.PolicyStatement(
                    effect=aws_iam.Effect.ALLOW,
                    actions=[
                        "kms:Decrypt",
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:DescribeKey",
                        "kms:GenerateDataKey",
                    ],
                    resources=[f"arn:aws:kms::{account}:*"],
                ),
                aws_iam.PolicyStatement(
                    effect=aws_iam.Effect.ALLOW,
                    actions=[
                        "s3:GetObject",
                        "s3:GetObjectAcl",
                        "s3:ListBucket",
                    ],
                    resources=[
                        f"{artifacts_bucket.bucket_arn}/*",
                        f"{artifacts_bucket.bucket_arn}",
                    ],
                ),
            ],
        )

        # FullAccess IAM Policy
        fullaccess_policy = aws_iam.ManagedPolicy(
            self,
            id="fullaccess_policy",
            managed_policy_name=f"{project_name}-{deployment_name}-{module_name}-{region}-{account}-full-access",
            statements=[
                aws_iam.PolicyStatement(
                    effect=aws_iam.Effect.ALLOW,
                    actions=[
                        "kms:Decrypt",
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:DescribeKey",
                        "kms:GenerateDataKey",
                    ],
                    resources=[f"arn:aws:kms::{account}:*"],
                ),
                aws_iam.PolicyStatement(
                    effect=aws_iam.Effect.ALLOW,
                    actions=[
                        "s3:GetObject",
                        "s3:GetObjectAcl",
                        "s3:ListBucket",
                    ],
                    resources=[
                        f"{artifacts_bucket.bucket_arn}/*",
                        f"{artifacts_bucket.bucket_arn}",
                    ],
                ),
                aws_iam.PolicyStatement(
                    actions=["s3:PutObject", "s3:PutObjectAcl"],
                    resources=[
                        f"{artifacts_bucket.bucket_arn}/*",
                        f"{artifacts_bucket.bucket_arn}",
                    ],
                ),
            ],
        )

        self.artifacts_bucket = artifacts_bucket
        self.logs_bucket = logs_bucket
        self.readonly_policy = readonly_policy
        self.fullaccess_policy = fullaccess_policy

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        suppressions = [
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-S1",
                    "reason": "Logging has been disabled for demo purposes",
                }
            ),
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-IAM5",
                    "reason": "Resource access restriced to IDF resources",
                }
            ),
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-IAM4",
                    "reason": "Resource access restriced to IDF resources",
                }
            ),
        ]

        NagSuppressions.add_stack_suppressions(self, suppressions)
