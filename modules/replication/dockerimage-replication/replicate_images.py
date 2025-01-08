# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import boto3
import subprocess
import time
import sys
import os
import json
from typing import Dict, Any, Optional
from replication_utils.utils import get_credentials
from replication_utils.logging import logger

successful_replication=[]
failed_replication=[]

aws_region = os.getenv("AWS_DEFAULT_REGION")
aws_account_id = os.getenv("AWS_ACCOUNT_ID")
repo_secret = os.getenv("SEEDFARMER_PARAMETER_HELM_REPO_SECRET_NAME", None)
repo_key = os.getenv("SEEDFARMER_PARAMETER_HELM_REPO_SECRET_KEY", None)
# Set AWS domain based on partition
aws_partition = os.getenv("AWS_PARTITION", "aws")
aws_domain = "amazonaws.com" if aws_partition == "aws" else "amazonaws.com.cn"



ecr_client = boto3.client("ecr", region_name=aws_region)

# Login to ECR
def login_to_ecr(account_id):
    login_cmd = [
        "aws", "ecr", "get-login-password", "--region", aws_region
    ]
    password = subprocess.check_output(login_cmd).decode("utf-8")
    docker_login_cmd = [
        "docker", "login", "--username", "AWS", "--password-stdin", 
        f"{account_id}.dkr.ecr.{aws_region}.{aws_domain}"
    ]
    subprocess.run(docker_login_cmd, input=password.encode("utf-8"), check=True)

# Check if repository exists
def repository_exists(repo_name):
    try:
        ecr_client.describe_repositories(repositoryNames=[repo_name])
        return True
    except ecr_client.exceptions.RepositoryNotFoundException:
        return False

# Create repository
def create_repository(repo_name):
    ecr_client.create_repository(
        repositoryName=repo_name,
        imageScanningConfiguration={"scanOnPush": True}
    )
    time.sleep(2)

# Pull and push Docker image
def pull_and_push_image(src_repo, src, target_ecr_tag, username=None, password=None):
    if username and password:
        login_cmd = ["docker", "login", "-u", username, "-p", password, src]
        subprocess.run(login_cmd, check=True)
    subprocess.run(["docker", "pull", src], check=True)
    subprocess.run(["docker", "tag", src, target_ecr_tag], check=True)
    subprocess.run(["docker", "push", target_ecr_tag], check=True)
    subprocess.run(["docker", "rmi", src], check=True)

# Check if image exists in ECR
def image_exists(repo_name, image_tag):
    try:
        response = ecr_client.batch_get_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": image_tag}],
        )
        return any(img["imageId"]["imageTag"] == image_tag for img in response.get("images", []))
    except ecr_client.exceptions.ImageNotFoundException:
        return False

# Create workflow
def create(image_repl: Dict[str, str], repo_user:Optional[str]=None,repo_pwd:Optional[str]=None ):
    
    try:
        src = image_repl["src"]
        target = image_repl["target"]
        src_info = src.split(":")
        src_repo = src_info[0]
        src_version = src_info[1]
        
        target_info = target.split(":")
        target_repo = target_info[0]
        if target_repo.startswith(f"{aws_account_id}.dkr.ecr"):
            s = target_repo.split('/')
            target_repo = "/".join(s[1:])
        
        target_version = target_info[1]
                
        if not repository_exists(target_repo):
            logger.info(f"{target_repo} not found in ECR. Creating...")
            create_repository(target_repo)
        else:
            logger.info(f"{target_repo} found in ECR")

        if not image_exists(target_repo, target_version):
            logger.info(f"{target_repo}:{target_version} not found, fetching")
            pull_and_push_image(src_repo, src, target, repo_user, repo_pwd)
        else:
            logger.info(f"{target_version} found in {target_repo}, skipping replication")
    except Exception as e:
        logger.info(f"Error: {e}")
        failed_replication.append(image_repl)
        return
    successful_replication.append(image_repl)


# Main entry point
if __name__ == "__main__":
    input_file = "./updated_images.json"
    

    # Check if the input file exists
    if not os.path.isfile(input_file):
        logger.info(f"Error: {input_file} not found!")
        sys.exit(1)

    image_data = {}
    # Load JSON data
    with open(input_file, "r") as f:
        image_data = json.load(f)
    # Log in to the source repository
    repo_user, repo_password = get_credentials(repo_secret, repo_key)
    if not repo_user or not repo_password:
        logger.info("Not using any auth for source repos for images")
        repo_user, repo_password = None, None
        
    try:
        login_to_ecr(aws_account_id)
    except:
        logger.info("Cannot log into ECR, stopping the replication entirely")
        exit(1)

    for image_repl in image_data:
        create(image_repl,repo_user, repo_password)
        
    logger.info("Successfully replicated images")
    for im in successful_replication:
        logger.info(f"    {json.dumps(im, indent=2)}")

    logger.info("FAILED replicated image")
    for imf in failed_replication: 
        logger.info(f"    {json.dumps(imf, indent=2)}")

    logger.info("Script completed.")

