# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional

import cdk_nag
from aws_cdk import Aspects, Duration, RemovalPolicy, Stack
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_kms as kms
from constructs import Construct

IMAGE_MUTABILITY = {
    "IMMUTABLE": ecr.TagMutability.IMMUTABLE,
    "MUTABLE": ecr.TagMutability.MUTABLE,
}
ENCRYPTION = {
    "AES256": ecr.RepositoryEncryption.AES_256,
    "KMS_MANAGED": ecr.RepositoryEncryption.KMS,
    "KMS_CUSTOM": ecr.RepositoryEncryption.KMS,
}


class EcrStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repository_name: str,
        image_tag_mutability: str,
        lifecycle_max_image_count: Optional[str],
        lifecycle_max_days: Optional[str],
        removal_policy: Optional[str],
        image_scan_on_push: bool,
        encryption: str,
        kms_key_arn: Optional[str],
        **kwargs: Optional[Any],
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repository = ecr.Repository(
            self,
            f"{repository_name}",
            repository_name=repository_name,
            image_tag_mutability=IMAGE_MUTABILITY[image_tag_mutability],
            removal_policy=RemovalPolicy.DESTROY if removal_policy in ["DESTROY"] else RemovalPolicy.RETAIN,
            empty_on_delete=True if removal_policy in ["DESTROY"] else False,
            image_scan_on_push=image_scan_on_push,
            encryption=ENCRYPTION[encryption],
            encryption_key=kms.Key.from_key_arn(self, "Key", key_arn=kms_key_arn)
            if encryption == "KMS_CUSTOM" and kms_key_arn
            else None,  # use AWS-managed KMS key if not provided
        )
        self.lifecycle_max_days = lifecycle_max_days
        self.lifecycle_max_image_count = lifecycle_max_image_count

        if lifecycle_max_days is not None:
            self.repository.add_lifecycle_rule(max_image_age=Duration.days(int(lifecycle_max_days)))

        if lifecycle_max_image_count is not None:
            self.repository.add_lifecycle_rule(max_image_count=int(lifecycle_max_image_count))

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
