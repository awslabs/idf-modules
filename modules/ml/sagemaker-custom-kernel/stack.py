# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any

import cdk_nag
from aws_cdk import Aspects, Stack
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk.aws_ecr_assets import DockerImageAsset
from cdk_ecr_deployment import DockerImageName, ECRDeployment
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct


class CustomKernelStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        app_prefix: str,
        sagemaker_image_name: str,
        ecr_repo_name: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR Image deployment
        repo = ecr.Repository.from_repository_name(self, id=f"{app_prefix}-ecr-repo", repository_name=ecr_repo_name)

        local_image = DockerImageAsset(
            self,
            "ImageExtractionDockerImage",
            directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), f"docker/{sagemaker_image_name}"),
        )

        self.image_uri = f"{repo.repository_uri}:latest"
        ECRDeployment(
            self,
            "ImageURI",
            src=DockerImageName(local_image.image_uri),
            dest=DockerImageName(self.image_uri),
        )

        # SageMaker Studio Image Role
        self.sagemaker_studio_image_role = iam.Role(
            self,
            f"{app_prefix}-image-role",
            role_name=f"{app_prefix}-image-role",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )
        self.sagemaker_studio_image_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
        )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
        NagSuppressions.add_stack_suppressions(
            self,
            apply_to_nested_stacks=True,
            suppressions=[
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM4",
                        "reason": "Image Role needs Sagemaker Full Access",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM5",
                        "reason": "ECR Deployment Service Role needs Full Access",
                    }
                ),
            ],
        )
