# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

=======

## UNRELEASED

### **Added**

### **Changed**

### **Removed**

=======

## v1.2.0 (2023-11-09)

### **Added**

- added `sagemaker-studio` module with unit-tests
- enforced TLS version 1.2, node-node encryption and encryption at rest on OS module
- added `emr-serverless` module with unit-tests
- added workflow entries to all IDF modules
- made `requirements.txt` file of MWAA configurable via a user defined entry from module manifest file
- added `app-registry` module for being able to scrape app-specific CloudFormation stacks for AWS Solutions
- added `app-insights` integration with app-registry module to derive additional insights from the associated resources in the resource group
- added dynamic stack naming based on Solution Info:
  - modules/compute/aws-batch
  - modules/compute/emr-serverless
  - modules/network/basic-cdk
  - modules/orchestration/mwaa
  - modules/service-catalog/app-registry
  - modules/storage/buckets
  - modules/storage/opensearch
- added ability for artifact buckets to write events to event bridge.
- added eks node iam role that all eks nodes will assume on start

### **Changed**

- replaced exporting metadata with seedfarmer command
- storage/buckets - added `usedforsecurity=False` to the sha1 creation of bucket names
- applying changes based off security scans and code standards recommendations
- `data/mwaa/requirements/requirements-emr-serverless.txt` updated `Pillow~=9.3.0` as per bot
- changed the `data/mwaa/requirements/requirements-emr-serverless.txt` to support Amazon MWAA 2.6.3 version
- added paginatior for CFN list stacks to scrape the stacks starting with `addf` for registering the apps to appregistry
- updated `Pillow~=10.0.1` in `mwaa/requirements/requirements*.txt` and in `data/mwaa/requirements/requirements-emr-serverless.txt`
- reduced the length of s3 bucket name for docker images replication to fix failures caused due to naming length
- added logic to validate relative paths in `storage/fsx-lustre` module, accept `fsx-version` input parameter
- added logic to require IMDSv2 in eks nodes

### **Removed**

=======

## v1.1.0 (2023-06-27)

### **Added**

- adding individual module unit tests, hooked up to workflows
- added EFS and Opensearch modules, refactored them to be agnostic of a project with unit-tests
- added `isolated` subnets feature to networking module
- fixed the way `internet_accessible` bool is referenced
- added `manifests/local` for local testing and `examples/manifests/example` as a guidance for calling the modules using `git paths`
- added contributing guidance to `CONTRIBUTING.md`
- refactored AWS Batch module, to be agnostic of a project with unit-tests
- refactored Amazon MWAA module, to be agnostic of a project with unit-tests
- refactored Fsx-Lustre module, to be agnostic of a project with unit-tests
- refactored Neptune module, to be agnostic of a project with unit-tests
- added module output example for `dummy/blank` module
- added EKS module, refactored it to be agnostic of a project with unit-tests
- added Docker images replication module, refactored it to be agnostic of a project with unit-tests

### **Changed**

- refactored L1 cdk implementation of networking -> interface endpoints creation with the L2 mode
- added `version locking to neptune engine` to avoid cdk deployment errors
- bumped CDK versions to avoid the issue of nodejs12.x deprecation
- removed `jq` from OS module

### **Removed**

## v1.0.0 (2023-03-15)

### **Added**

- initialization of repo with `modulesptionals/network/basic-cdk` and `modules/storage/buckets`
- adding `modules/dummy/blank`