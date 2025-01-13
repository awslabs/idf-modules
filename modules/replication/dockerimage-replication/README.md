## Introduction

Docker Images replication

### Description

This module helps with replicating Docker images from the list of provided helm charts and any docker image from a public registry into an AWS account's Private ECR. For deploying EKS module or any container related apps in isolated subnets (which has access to AWS APIs via Private endpoints), the respective docker images should be available internally in an ECR repo as a pre-requisiste. This module will generate a `.txt` file which will be populated with list of `to-be-replicated` docker images and the seedfarmer's `deployspec.yaml` invokes the replication.

***CLEANUP***

The cleanup workflow invokes a python script which deletes the replicated docker images from ECR whose prefix starts with `project_name`. This may cause issues if the replicated images are being used by other applications in the same/cross account. The current `deployspec.yaml` doesnt call the python script to cleanup the images, however an end-user can evaluate the need/risk associated and uncomment the relevant instruction under `destroy` phase.

### Input Parameters

#### Required Parameters

- `eks_version`: The EKS Cluster version to lock the version to

#### Optional Parameters

- `HelmRepoSecretName`:
- `HelmRepoSecretKey`:  
- `HelmDistroSecretName`: 
- `HelmDistroUrl`: 
- `HekmDistroSecretKey`:


#### Required Files

- `dataFiles`: The docker replication module consumes the EKS version specific helm charts inventory to replicate the docker images

#### Manifest Example declaration

```yaml
name: replication
#path: modules/replication/dockerimage-replication/
path: git::https://github.com/awslabs/idf-modules.git//modules/replication/dockerimage-replication?ref=release/1.13.0
dataFiles:
  - filePath: data/eks_dockerimage-replication/versions/1.29.yaml
  - filePath: data/eks_dockerimage-replication/versions/default.yaml
parameters:
  - name: eks-version
    value: "1.29"
  - name: HelmRepoSecretName
    value: replicationbmw
  - name: HelmDistroSecretName
    value: replicationbmw
  - name: HelmDistroUrl
    value: https://somehostedurl.com/something/relativeurl/helm-v3.11.3-linux-amd64.tar.gz

```

### Module Metadata Outputs

```json
{
  "repl": {
    "S3Bucket": "idftest-dkr-img-rep-md-us-east-1-123456789012",
    "S3FullPath": "idftest-dkr-img-rep-md-us-east-1-123456789012/repltestrepl-repl-repl-metadata.json",
    "S3Object": "repltestrepl-repl-repl-metadata.json",
    "s3_bucket": "idftest-dkr-img-rep-md-us-east-1-123456789012", // For backard compatability
    "s3_full_path": "idftest-dkr-img-rep-md-us-east-1-123456789012/repltestrepl-repl-repl-metadata.json", // For backard compatability
    "s3_object": "repltestrepl-repl-repl-metadata.json" // For backard compatability
  }
}
```


