# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0


from typing import Optional

# https://docs.aws.amazon.com/eks/latest/userguide/add-ons-images.html
ECR_REGION_REGISTRY_MAP = {
    "af-south-1": "877085696533",
    "ap-east-1": "707767160287",
    "ap-northeast-1": "602401143452",
    "ap-northeast-2": "602401143452",
    "ap-northeast-3": "602401143452",
    "ap-south-1": "602401143452",
    "ap-southeast-1": "602401143452",
    "ap-southeast-2": "602401143452",
    "ca-central-1": "602401143452",
    "eu-central-1": "602401143452",
    "eu-north-1": "602401143452",
    "eu-south-1": "590381155156",
    "eu-west-1": "602401143452",
    "eu-west-2": "602401143452",
    "eu-west-3": "602401143452",
    "sa-east-1": "602401143452",
    "us-east-1": "602401143452",
    "us-east-2": "602401143452",
    "us-west-1": "602401143452",
    "us-west-2": "602401143452",
    "cn-north-1": "918309763551",
    "cn-northwest-1": "961992271922",
}


def fetch_global_ecr_account(region: str) -> Optional[str]:
    if region in ECR_REGION_REGISTRY_MAP.keys():
        return ECR_REGION_REGISTRY_MAP.get(region)
    else:
        raise ValueError(
            f"Invalid region: {region} found while fetching the Global ECR account."
            " Please update ECR_REGION_REGISTRY_MAP to onboard your region"
        )
