# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#!/bin/bash

set -euo pipefail
set +x

# Check AWS Domain
if [[ $AWS_PARTITION == "aws" ]]; then
    export AWS_DOMAIN="amazonaws.com"
else
    export AWS_DOMAIN="amazonaws.com.cn"
fi

# Login to ECR
login_to_ecr() {
    local account_id="$1"
    aws ecr get-login-password --region "$AWS_DEFAULT_REGION" | docker login --username AWS --password-stdin "$account_id.dkr.ecr.$AWS_DEFAULT_REGION.$AWS_DOMAIN"
}

# check if the repository exists
repository_exists() {
    local repo_name="$1"
    aws ecr describe-repositories --repository-names "$repo_name" > /dev/null 2>&1
}

# create an AWS ECR
create_repository() {
    local repo_name="$1"
    aws ecr create-repository --repository-name "$repo_name" --image-scanning-configuration scanOnPush=true
    sleep 10
}

# pull and push images
pull_and_push_image() {
    local image="$1"
    local target_ecr_tag="$2"
    docker pull "$image"
    docker tag "$image" "$target_ecr_tag"
    docker push "$target_ecr_tag"
    docker rmi "$image"
}

# check if the container image exists
image_exists() {
    local repo_name="$1"
    local image_tag="$2"
    aws ecr batch-get-image --repository-name "$repo_name" --image-ids "imageTag=$image_tag" --query 'images[].imageId.imageTag' --output text | grep -q "$image_tag"
}

create() {
    # Iterate through the list of images
    while IFS="" read -r image || [ -n "$image" ]
    do
    image_name=$(echo $image | awk -F ':' '{ print $1 }')
    image_tag=$(echo $image | awk -F ':' '{ print $2 }')
    if ( [[ ${image_name} =~ ^[0-9] ]] ); then
        IMAGE_ACCOUNT_ID=$(echo $image_name | awk -F '/' '{print $1}' | awk -F '.' '{print $1}')
        login_to_ecr $IMAGE_ACCOUNT_ID
    fi

    TARGET_REPOSITORY_NAME=${SEEDFARMER_PROJECT_NAME}-${image_name}
    TARGET_ECR_TAG=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.${AWS_DOMAIN}/$TARGET_REPOSITORY_NAME:${image_tag}

    if ! repository_exists "$TARGET_REPOSITORY_NAME"; then
        echo "$TARGET_REPOSITORY_NAME not found in ECR. Creating..."
        create_repository "$TARGET_REPOSITORY_NAME"
    else
        echo "$TARGET_REPOSITORY_NAME found in ECR"
    fi

    login_to_ecr $AWS_ACCOUNT_ID

    if ! image_exists "$TARGET_REPOSITORY_NAME" "$image_tag"; then
        echo "$TARGET_REPOSITORY_NAME:$image_tag not found, fetching"
        pull_and_push_image "$image" "$TARGET_ECR_TAG"
    else
        echo "$image_tag found in $TARGET_ECR_TAG skipping replication"
    fi

    done < images.txt
}

destroy() {
    echo "WARNING: The destroy workflow removes the ECR repositories which we were created during replication"
    python delete-repos.py ${SEEDFARMER_PROJECT_NAME}
}

"$@"
