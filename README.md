# Industry Dataframework (IDF)

IDF is a collection of resuable Infrastructure as Code (IAC) modules that works with [SeedFarmer CLI](https://github.com/awslabs/seed-farmer). Please see the [DOCS](https://seed-farmer.readthedocs.io/en/latest/) for all things seed-farmer.

The modules in this repository are decoupled from each other and can be aggregated together using GitOps (manifest file) principles provided by `seedfarmer` and achieve the desired use cases. It removes the undifferentiated heavy lifting for an end user by providing hardended modules and enables them to focus on building business on top of them.

## General Information

The modules in this repository are / must be generic for resuse without affiliation to any one particular project or use case or any vertical.

All modules in this repository adhere to the module strutucture defined in the the [SeedFarmer Guide](https://seed-farmer.readthedocs.io/en/latest)

- [Project Structure](https://seed-farmer.readthedocs.io/en/latest/project_development.html)
- [Module Development](https://seed-farmer.readthedocs.io/en/latest/module_development.html)
- [Module Manifest Guide](https://seed-farmer.readthedocs.io/en/latest/manifests.html)

## Modules supported by IDF

### Networking Modules

| Type | Description |
| --- | --- |
|  [Networking Module](modules/network/basic-cdk/README.md)  |  Deploys standard networking resources such as VPC, Public/Private/Isolated subnets and Interface/Gateway endpoints   |

### Compute Modules

| Type | Description |
| --- | --- |
|  [EKS Module](modules/compute/eks/README.md)  |  Deploys EKS Cluster with the documented list of addons  |
|  [AWS Batch Module](modules/compute/aws-batch/README.md)  |  Deploys AWS Batch resources   |

### Database Modules

| Type | Description |
| --- | --- |
|  [Neptune Module](modules/database/neptune/README.md)  |  Deploys Amazon Managed Neptune Cluster   |

### Storage Modules

| Type | Description |
| --- | --- |
|  [Opensearch Module](modules/storage/opensearch/README.md)  |  Deploys Amazon Opensearch Cluster   |
|  [S3 Buckets Module](modules/storage/buckets/README.md)  |  Deploys AWS S3 buckets for logging and artifacts purpose   |
|  [EFS Module](modules/storage/efs/README.md)  |  Deploys Amazon EFS for shared artifacts purpose   |
|  [FSX-Lustre Module](modules/storage/fsx-lustre/README.md)  |  Deploys Amazon FSX Lustre for HPC/Bigdata workloads   |

### Orchestration Modules

| Type | Description |
| --- | --- |
|  [Amazon Managed Workflows for Apache Airflow (MWAA) Module](modules/orchestration/mwaa/README.md)  |  Deploys an Amazon MWAA module   |

### Replication Modules

| Type | Description |
| --- | --- |
|  [DockerImages Replication Module](modules/replication/dockerimage-replication/README.md)  |  Deploys docker images replication module which replicates any docker image from public registry to an internal ECR repo(s)   |
