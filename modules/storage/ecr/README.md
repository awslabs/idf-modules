# ECR Module

## Description

This module creates Amazon Elastic Container Registry Repository.

## Inputs/Outputs

### Input Paramenters

#### Required

None

#### Optional

- `repository-name`: Repository name. Defaults to `{project_name}-{deployment_name}-{module-name}-ecr"`
- `image-tag-mutability`: Image tag mutability. Defaults to `"IMMUTABLE"`. Possible values: `"IMMUTABLE"` or `"MUTABLE"`
- `lifecycle-max-days`: Max days to store the images in ECR. Defaults to `None`, (no removal of images)
- `lifecycle-max-image-count`: Max images to store the images in ECR. Defaults to `None`, (no removal of images)
- `image-scan-on-push`: enable image scan on push. Defaults to `False` (manual scan)
- `removal-policy` - the retention policy to put on the EFS service
  - defaults to `RETAIN`
  - supports `DESTROY` and `RETAIN` only
- `encryption` - encryption mode
  - defaults to `AES256`
  - supports `AES256` and `KMS` only
- `kms-key-arn` - KMS key ARN to use for encryption. If `encryption` is `KMS` and no key ARN provided, use AWS-managed KMS key

### Module Metadata Outputs

- `EcrRepositoryName`: ECR repository name
- `EcrRepositoryArn`: ECR repository ARN

#### Output Example

```json
{
    "EcrRepositoryName": "pytorch-10",
    "EcrRepositoryArn": "arn:aws:ecr:<REGION>:<ACCOUNT_ID>:repository/pytorch-10"
    }

```
