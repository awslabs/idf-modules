# OpenSearch Serverless

## Description

This module creates a Serverless OpenSearch cluster for use in IDF

## Inputs/Outputs

### Input Paramenters

#### Required

- `vpc-id`: The VPC-ID that the cluster will be created in
- `private-subnet-ids`: The private subnets that the cluster will be created in

#### Optional

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
