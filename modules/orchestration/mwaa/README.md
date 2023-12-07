# Amazon Managed Workflows for Apache Airflow (MWAA)

## Description

This module:

- creates an Amazon Managed Airflow Environment to execute DAGs created by other modules
- creates an IAM Role (the MWAA Execution Role) with least privilege permissions
- *Optionally* creates an S3 Bucket to store DAG artifacts

## Limitations

When deploying an MWAA environemnt, an S3 bucket is used to store supporting files such as `requirements`, `plugins` and `dags`.  This module will create a bucket if not one provided in the parameter `dag-bucket-name`.  IDF does support multiple MWAA modules in a single deployment, but due to the nature of how MWAA is managed at AWS, MWAA modules CANNOT SHARE the buckets that store the `requirements`, `plugins` or `dags`.  EACH MWAA module deployed requires a separate bucket for these artifacts.

In other words, if the `dag-bucket-name` is `MY_AWESOME_BUCKET_NAME` then ONLY ONE MWAA module can refer to that bucket to store `dags` (as well as `plugins` and `requirements`).  So, pick a unique bucket per MWAA module deployment.  

## Inputs/Outputs

### Input DataFiles

#### Required

NA

#### Optional

- `dataFiles`: User can optionally provide `filePath` reference to a custom airflow requirements.txt file(available locally/remote) and should make sure to provide the value of the filepath as an environment variable under `Parameters`. Following is the reference implementation using dataFiles:
- `solution-id`: a unique identifier for this deployment (must be used with `solution-description`)
- `solution-name`: a unique name for this deployment (must be used with `solution-id`)
- `solution-version`: a unique version for this deployment

```yaml
name: mwaa
path: modules/orchestration/mwaa/
dataFiles:
  - filePath: data/mwaa/requirements/requirements-emr-serverless.txt
parameters:
  - name: custom-requirements-path
    value: data/mwaa/requirements/requirements-emr-serverless.txt

```

### Input Paramenters

#### Required

- `vpc-id`: VPC Id where the MWAA Environment will be deployed
- `private-subnet-ids`: List of Private Subnets Ids where the MWAA Environment will be deployed

#### Optional

- `dag-bucket-name`: name of the S3 Bucket to configure the MWAA Environment to monitor for DAG artifacts. An S3 Bucket is created if none is provided
- `dag-path`: path in the S3 Bucket to configure the MWAA Environment to monitor for DAG artifacts. Defaults to `dags` if none is provided
- `environment-class`: the MWAA Environement Instance Class. Defaults to `mw1.small` if none is provided
- `max-workers`: the Maximum number of workers to configure the MWAA Environment to allow. Defaults to `25` if none is provided
- `airflow-version`: The Airflow version you would want to set in the module. It is defaulted to `2.5.1`
- `mwaa-requirements-file` - Support for customized requiremements file installed on MWAA
  - ANY file referenced MUST be located `modules/core/mwaa/requirements/*.txt` and be python requirements compliant
  - in if not provided, default is `requirements.txt`

### Module Metadata Outputs

- `DagBucketName`: name of the S3 Bucket configured to store MWAA Environment DAG artifacts
- `DagPath`: name of the path in the S3 Bucket configured to store MWAA Environment DAG artifacts
- `MwaaExecRoleArn`: ARN of the MWAA Execution Role created by the Stack

#### Output Example

```json
{
    "DagBucketName": "some-bucket",
    "DagPath": "dags",
    "MwaaExecRoleArn": "arn:::::"
}
```