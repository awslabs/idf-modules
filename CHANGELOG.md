# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## UNRELEASED

### **Added**

- feat: Adds Integration Tests Module
- moved module `integration/fsx-lustre-on-eks` into repo from [ADDF-Modules repo](https://github.com/awslabs/autonomous-driving-data-framework)
- added support for AWS LocalZone Public and Private Subnets
- added support for bedrock endpoints
- added support for EKS Self Managed node groups with autoscaling
- added `emr-on-eks` module and made it generic

### **Changed**

- fix: `storage/buckets` Correct issues with bucket names above character limit
- chore: mwaa dags bucket auto delete objects
- set Pillow version to 10.3.0 as per bot recommendation
- `storage/ecr` set `auto_delete_images` to `True` when removal policy is **DESTROY**
- refactored `fix.sh` script to use `ruff` instead of `black` and `isort`
- refactored eks module, fixed the breaking nginx ingress and made more least privileged
- fixed `urlib3` version as per dependabot alert
- bumped seedfarmer version to `4.0.1`

### **Removed**

=======

=======

## v1.6.0 (2024-05-02)

### **Added**

- added KMS/AES encryption and image scan on push to `ecr` module
- exporting `kubectl lambda iam role arn` for running kubectl calls from the downstream stacks

### **Changed**

- upgraded `vpc-cni` version to `1.18.0` to support EKS 1.29 version
- EKS README.md doc fixes

### **Removed**

=======

=======

## v1.6.0 (2024-04-02)

### **Added**

- added support for AWS CloudWatch Observability Managed Addon
- added support for GPU AMIs using `use_gpu_ami` flag
- made `mountpoint for s3` driver configurable to work with s3 buckets on fly

### **Changed**

- update MySQL instance to use T3 instance type

### **Removed**

- cleaned up CNI metrics as its no longer used

=======

=======

## v1.5.0 (2024-03-19)

### **Added**

- added support for Elastic Kubernetes cluster 1.26 version
- added support for Elastic Kubernetes cluster 1.29 version

### **Changed**

- made the `storage-capacity` configurable on the `fsx-lustre` module
- in `mwaa` module, moving creation of plugins.zip to the deployspec since shutil errors out in python 3.11.6
- fix the CDK nag suppressions in the `rds` module
- adding removal-policy support for `ecr` module
- added taint support (`eks_node_taints`) for node groups
- set Pillow version to 10.2.0 as per bot recommendation

### **Removed**

=======

=======

## v1.4.1 (2024-03-01)

### **Added**

### **Changed**
- modified `fsx-lustre` module to auto-import data if configured

### **Removed**


=======



=======

## v1.4.0 (2024-02-27)

### **Added**

- added Opensearch serverless module
- updated replication module to avoid docker pull rate limits and resource creation race conditions
- added RDS database module

### **Changed**

- added `database-name` and `accessible-from-vpc` parameters to RDS module

### **Removed**

- removed SageMaker Studio module that moved to [MLOps Modules](https://github.com/awslabs/mlops-modules)

=======

=======

## v1.3.0 (2024-01-16)

### **Added**

- added eks node iam role that all eks nodes will assume on start
- added support for S3 CSI driver

### **Changed**

- added logic to require IMDSv2 in eks nodes
- regrouped ecr module from `containers` to `storage` group
- fixed the execution of workflow logic to remove an additional `/`

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
