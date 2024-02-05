# OpenSearch Serverless

## Description

This module creates an  Amazon OpenSearch Serverless (AOSS) cluster for use in IDF

## Inputs/Outputs

### Input Paramenters

#### Required

- `vpc-id`: The VPC-ID that the cluster will be created in
- `private-subnet-ids`: The private subnets that the cluster will be created in

#### Optional

AOSS's [default](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-scaling.html#serverless-scaling-limits) maximum capacity is 10 OCUs for indexing and 10 OCUs for search. The minimum allowed capacity for an account is 2 OCUs for indexing and 2 OCUs for search. You can always enforce limits at an account level using AWS CLI or any suppoprted SDKs.

As an example, you can follow the [docs](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-scaling.html#serverless-scaling-configure) here, and add the relevant AWS CLI command in the deployspec.yaml to enforce the capacity settings. Also make sure to update the modulestack.yaml with the necessary IAM permissions to make the relevant API call(s).

### Sample manifest declaration

```yaml
name: opensearch-s
path: modules/storage/opensearch-serverless #Alternatively gitpath can be used for remote deployment of this module
parameters:
  - name: vpc-id
    valueFrom:
      moduleMetadata:
        group: networking
        name: basic-networking
        key: VpcId
  - name: private-subnet-ids
    valueFrom:
      moduleMetadata:
        group: networking
        name: basic-networking
        key: PrivateSubnetIds
```

### Module Metadata Outputs

- `OpenSearchCollectionEndpoint`: the collection endpoint of Serverless AWS OpenSearch
- `OpenSearchDashboardEndpoint`: URL of the OpenSearch cluster dashboard
- `OpenSearchCollectionSecurityGroupId`: the security group associated with Serverless AWS OpenSearch

#### Output Example

```json
{
  "OpenSearchDashboardEndpoint": "https://XXXXXXXXXXXXX.us-west-2.aoss.amazonaws.com/_dashboards",
  "OpenSearchCollectionEndpoint": "https://XXXXXXXXXXXXX.us-west-2.aoss.amazonaws.com",
  "OpenSearchCollectionSecurityGroupId": "sg-XXXXXXX"
}

```
