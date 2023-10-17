# OpenSearch


## Description

This module creates an OpenSearch cluster for use in IDF


## Inputs/Outputs

### Input Paramenters

#### Required

- `vpc-id`: The VPC-ID that the cluster will be created in
- `private-subnet-ids`: The private subnets that the cluster will be created in

#### Optional

- `opensearch_data_nodes`: The number of data nodes, defaults to `1`
- `opensearch_data_nodes_instance_type`: The data node type, defaults to `r6g.large.search`
- `opensearch_master_nodes`: The number of master nodes, defaults to `0`
- `opensearch_master_nodes_instance_type`: The master node type, defaults to `r6g.large.search`
- `opensearch_ebs_volume_size`: The EBS volume size (in GB), defaults to `10`
- `solution-id`: a unique identifier for this deployment (must be used with `solution-description`)
- `solution-name`: a unique name for this deployment (must be used with `solution-id`)
- `solution-version`: a unique version for this deployment

### Module Metadata Outputs

- `OpenSearchDomainEndpoint`: the endpoint name of the OpenSearch Domain
  `OpenSearchDomainName`: the name of the OpenSearch Domain
- `OpenSeearchDashboardUrl`: URL of the OpenSearch cluster dashboard
- `OpenSearchSecurityGroupId`: name of the DDB table created for Rosbag Scene Data

#### Output Example

```json
{
  "OpenSearchDashboardUrl": "https://vpc-idf-test-core-opensearch-aaa.us-east-1.es.amazonaws.com/_dashboards/",
  "OpenSearchDomainName": "vpc-idf-test-core-opensearch-aaa",
  "OpenSearchDomainEndpoint": "vpc-idf-test-core-opensearch-aaa.us-east-1.es.amazonaws.com",
  "OpenSearchSecurityGroupId": "sg-XXXXXXX"
}

```
