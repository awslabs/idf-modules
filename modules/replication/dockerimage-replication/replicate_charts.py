# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import subprocess
import sys
import time
from replication_utils.utils import get_credentials
from replication_utils.logging import logger
successful_replication=[]
failed_replication=[]

account_id= os.getenv("AWS_ACCOUNT_ID")
region = os.getenv("AWS_DEFAULT_REGION")
repo_secret = os.getenv("SEEDFARMER_PARAMETER_HELM_REPO_SECRET_NAME", None)
repo_key = os.getenv("SEEDFARMER_PARAMETER_HELM_REPO_SECRET_KEY", None)
aws_partition = os.getenv("AWS_PARTITION", "aws")
aws_domain = "amazonaws.com" if aws_partition == "aws" else "amazonaws.com.cn"


def mask_sensitive_data(command):
    """Mask sensitive data like passwords in the command string."""
    if "--password" in command:
        parts = command.split("--password", 1)
        if len(parts) > 1:
            before_password = parts[0]
            after_password = parts[1].split(" ", 1)  # Split after the password
            if len(after_password) > 1:
                # Reassemble with masked password
                return f"{before_password}--password ****** {after_password[1]}"
            else:
                return f"{before_password}--password ******"
    return command

def run_command(command, capture_output=False):
    """Run a shell command."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=capture_output
        )
        return True
    except subprocess.CalledProcessError as e:
        # Sanitize the command to hide passwords
        sanitized_command = mask_sensitive_data(command)
        logger.info(f"Error running command: {sanitized_command}\n{e.stderr if capture_output else ''}")
        return False


def create_ecr_repo(repo_name):
    """Create an ECR repository if it doesn't exist."""
    logger.info(f"Checking if ECR repository '{repo_name}' exists...")
    command = f"aws ecr describe-repositories --repository-names {repo_name}"
    if not run_command(command):
        logger.info(f"ECR repository '{repo_name}' does not exist. Creating...")
        command = f"aws ecr create-repository --repository-name {repo_name}"
        if not run_command(command):
            logger.info(f"Error: Failed to create ECR repository '{repo_name}'.")
            return False
        logger.info(f"ECR repository '{repo_name}' created successfully.")
    else:
        logger.info(f"ECR repository '{repo_name}' already exists.")
    return True

def log_into_ecr():

    command= f"""aws ecr get-login-password \
     --region {region} | helm registry login \
     --username AWS \
     --password-stdin {account_id}.dkr.ecr.{region}.{aws_domain}
     """
    return run_command(f"{command}")

def process_chart(chart_key, chart_data):
    """Process a single chart from the JSON document."""
    logger.info(f"Processing chart: {chart_key}")


    # Extract Helm and repository details
    helm = chart_data["helm"]
    name = helm["name"]
    version = helm["version"]
    src_repository = helm["srcRepository"]
    target_repository = helm["repository"]

    # Log in to the source repository
    repo_user, repo_password = get_credentials(repo_secret, repo_key)
    if repo_user and repo_password:
        logger.info(f"Logging into source Helm repository: {src_repository}")
        helm_login_command = f"helm registry login {src_repository} --username {repo_user} --password {repo_password}"
        if not run_command(helm_login_command):
            logger.info(f"Error: Failed to log in to source Helm repository {src_repository}. Skipping {name}.")
            failed_replication.append(name)
            return

    # Pull the chart
    chart_path = f"{src_repository}/{name}"
    ## Assume that the helm has already updated the registry 
    logger.info(f"Pulling chart: {name} (Version: {version}) from {chart_path}")
    
    
    logger.info(f"helm pull {chart_key}/{name} --version {version}")
    
    if not run_command(f"helm pull {chart_key}/{name} --version {version}"):
        logger.info(f"Error: Failed to pull chart: {chart_key}/{name} Skipping.")
        failed_replication.append(name)
        return
    time.sleep(2)

    # Prepare for push
    chart_package = f"{name}-{version}.tgz"
    ecr_repo_name = f"{target_repository.replace('oci://', '').split('/', 1)[-1]}"
    ecr_repo_target = target_repository.replace(f"/{name}","")

    logger.info(f" {chart_package}  {ecr_repo_name}")

    # Create the ECR repository if needed
    if not create_ecr_repo(ecr_repo_name):
        logger.info(f"Error: Could not ensure ECR repository exists. Skipping {name}.")
        failed_replication.append(name)
        return
    time.sleep(2)

    # Push the chart to the target ECR repository
    logger.info(f"Pushing chart: {chart_package} to {ecr_repo_target}")

    if not run_command(f"helm push {chart_package} {ecr_repo_target}"):
        logger.info(f"Error: Failed to push chart: {ecr_repo_name}. Skipping.")
        failed_replication.append(name)
        return

    successful_replication.append(name)

    # Clean up local chart package
    logger.info(f"Cleaning up local chart package: {chart_package}")
    run_command(f"rm -f {chart_package}")

    logger.info(f"Successfully processed {name} -> {target_repository}")
    logger.info("------------------------------------------------")
    
    time.sleep(2)
    
def main():
    """Main function."""
    # Input JSON file
    input_file = "./replication-result.json"
    

    # Check if the input file exists
    if not os.path.isfile(input_file):
        logger.info(f"Error: {input_file} not found!")
        sys.exit(1)

    # Load JSON data
    with open(input_file, "r") as f:
        chart_data = json.load(f)

    charts = chart_data.get("charts", {})
    if not charts:
        logger.info("No charts found in the input JSON.")
        return

    # Enable OCI experimental feature in Helm
    os.environ["HELM_EXPERIMENTAL_OCI"] = "1"

    if not log_into_ecr():
        logger.info(f"Cannot log into account ECR, skipping everything")
        return

    # Process each chart
    for chart_key, chart_data in charts.items():
        process_chart(chart_key, chart_data)
        
    logger.info("Successfully replicated charts")
    for im in sorted(successful_replication):
        logger.info(f"    {im}")

    logger.info("FAILED replicated charts")
    for imf in sorted(failed_replication):
        logger.info(f"    {imf}")

    logger.info("Script completed.")


if __name__ == "__main__":
    main()
