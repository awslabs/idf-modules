# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python
import sys

import boto3
from botocore.exceptions import ClientError

ECR_CLIENT = boto3.client("ecr")
SSM_CLIENT = boto3.client("ssm")


def cleanup_ecr_repos(prefix: str) -> None:
    paginator = ECR_CLIENT.get_paginator("describe_repositories")
    for entry in paginator.paginate():
        for repo in entry["repositories"]:
            if repo["repositoryName"].startswith(prefix):
                print("Deleting ECR REPO: {}".format(repo["repositoryName"]))
                try:
                    ECR_CLIENT.delete_repository(repositoryName=repo["repositoryName"], force=True)
                except ClientError as ex:
                    if ex.response["Error"]["Code"] == "RepositoryNotFoundException":
                        print("Repository: {} is not found, no action needed".format(repo["repositoryName"]))
                        continue
                    else:
                        raise ex


# Cleanups ECR Repositories based on a prefix - ProjectName
cleanup_ecr_repos(prefix=sys.argv[1])
