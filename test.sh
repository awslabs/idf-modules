#!/bin/bash 
set -euo pipefail

# CDK_VERSION=${1}

# #relative to modules repo
# array=(
#     "networking/basic-cdk"
#     "storage/buckets"
# )


# for i in "${array[@]}"; do   # The quotes are necessary here
#     echo "$i"
#     npm install -g aws-cdk@${CDK_VERSION}
#     pip install -r requirements-dev.txt
#     pip install -r modules/$i/requirements.txt
#     pytest modules/$i --cov-config=modules/$i/coverage.ini --cov --cov-report=html:$CODEBUILD_SRC_DIR/reports/$i/html_dir --cov-report=xml:$CODEBUILD_SRC_DIR/reports/$i/coverage.xml
# done

####
while getopts c:m: flag
do
    case "${flag}" in
        c) CDK_VERSION=${OPTARG};;
        m) MODULE_PATH=${OPTARG};;
    esac
done

echo "CDK Version: $CDK_VERSION";
echo "Modules Path: $MODULE_PATH";

npm install -g aws-cdk@${CDK_VERSION}
pip install -r requirements-dev.txt
pip install -r modules/$MODULE_PATH/requirements.txt
pytest modules/$MODULE_PATH --cov-config=modules/$MODULE_PATH/coverage.ini --cov --cov-report=html:$CODEBUILD_SRC_DIR/reports/$MODULE_PATH/html_dir --cov-report=xml:$CODEBUILD_SRC_DIR/reports/$MODULE_PATH/coverage.xml

