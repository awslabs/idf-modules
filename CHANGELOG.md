# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

=======

## UNRELEASED

### **Added**

- enforced TLS version 1.2, node-node encryption and encryption at rest on OS module
 
### **Changed**

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