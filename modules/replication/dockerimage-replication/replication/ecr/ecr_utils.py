import subprocess
import time

import boto3

from replication.logging import logger


class ECRUtils:
    def __init__(self, aws_account_id: str, aws_region: str, aws_domain: str):
        self.aws_account_id = aws_account_id
        self.aws_region = aws_region
        self.aws_domain = aws_domain
        self.ecr_client = boto3.client("ecr", region_name=aws_region)

    def login_to_ecr(self, type: str = "docker") -> bool:
        get_password_cmd = ["aws", "ecr", "get-login-password", "--region", f"{self.aws_region}"]
        login_cmd_type = ["docker"]
        if type == "helm":
            login_cmd_type = ["helm", "registry"]

        login_cmd_tail = [
            "login",
            "--username",
            "AWS",
            "--password-stdin",
            f"{self.aws_account_id}.dkr.ecr.{self.aws_region}.{self.aws_domain}",
        ]
        login_cmd = login_cmd_type + login_cmd_tail
        auth_process = subprocess.Popen(get_password_cmd, shell=False, stdout=subprocess.PIPE)
        login_process = subprocess.run(
            login_cmd, stdin=auth_process.stdout, shell=False, capture_output=True, text=True
        )

        if login_process.returncode == 0:
            logger.info(f"ECR login for {type} successful: {login_process.stdout.strip()}")
            return True
        else:
            logger.info(f"ECR login for {type} failed: {login_process.stderr.strip()}")
            return False

    # Check if repository exists
    def repository_exists(self, repo_name: str) -> bool:
        try:
            self.ecr_client.describe_repositories(repositoryNames=[repo_name])
            return True
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            return False

    # Create repository
    def create_repository(self, repo_name: str) -> None:
        logger.info(f"Checking if ECR repository '{repo_name}' exists...")
        if not self.repository_exists(repo_name):
            logger.info(f"ECR repository '{repo_name}' does not exist. Creating...")
            self.ecr_client.create_repository(repositoryName=repo_name, imageScanningConfiguration={"scanOnPush": True})
            logger.info(f"ECR repository '{repo_name}' created successfully.")
            time.sleep(2)
        else:
            logger.info(f"ECR repository '{repo_name}' already exists.")

    # Check if image exists in ECR
    def image_exists(self, repo_name: str, image_tag: str) -> bool:
        try:
            response = self.ecr_client.batch_get_image(
                repositoryName=repo_name,
                imageIds=[{"imageTag": image_tag}],
            )
            return any(img["imageId"]["imageTag"] == image_tag for img in response.get("images", []))
        except self.ecr_client.exceptions.ImageNotFoundException:
            return False
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            return False

    def cleanup_ecr_repos(self, prefix: str) -> None:
        paginator = self.ecr_client.get_paginator("describe_repositories")
        for entry in paginator.paginate():
            for repo in entry["repositories"]:
                if repo["repositoryName"].startswith(prefix):
                    print("Deleting ECR REPO: {}".format(repo["repositoryName"]))
                    try:
                        self.ecr_client.delete_repository(repositoryName=repo["repositoryName"], force=True)
                    except self.ecr_client.exceptions.ClientError as ex:
                        if ex.response["Error"]["Code"] == "RepositoryNotFoundException":
                            print("Repository: {} is not found, no action needed".format(repo["repositoryName"]))
                            continue
                        else:
                            raise ex
