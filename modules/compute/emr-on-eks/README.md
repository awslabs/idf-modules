## Introduction

This module provisions EMR on EKS supporting infrastructure which creates EMR Vritual Cluster, K8s Namespace, EMR Job Execution Role which enables any spark applications to use Airflow to trigger spark jobs on EMR on EKS.

> Note: You should be adjusting the required permissions on EMR Job execution role to allow spark driver to write logs to CloudWatch and S3 logging bucket.

## Inputs/Outputs

### Input Parameters

#### Required

- `vpc-id`: The VPC-ID that the cluster will be created in
- `private-subnet-ids`: The Private Subnets that the AWS Batch Compute resources will be deployed to
- `eks-cluster-admin-role-arn`: The EKS Cluster's Master IAM Role Arn obtained from EKS Module metadata
- `eks-cluster-name`: The EKS Cluster Name obtained from EKS Module metadata
- `eks-oidc-arn`: The EKS Cluster's OIDC Arn for creating EKS Service Accounts obtained from EKS Module metadata
- `eks-openid-issuer`: The EKS Cluster's OPEN ID issuer
- `eks-handler-rolearn`: The EKS Lambda Handler IAM Role Arn
- `emr-eks-namespace`: The K8s namespace to which the EMR Virtual Cluster will be tied to
- `artifacts-bucket-name`: The artifacts bucket to which the datasets will be uploaded
- `logs-bucket-name`: The logs bucket to which you can configure the spark logs to be written to

#### Optional

### Sample declaration of Airflow with EMR on EKS

```yaml
name: emr-on-eks
path: modules/compute/emr-on-eks
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
        key: LocalZonePrivateSubnetIds
  - name: eks-cluster-admin-role-arn
    valueFrom:
      moduleMetadata:
        group: compute
        name: eks
        key: EksClusterMasterRoleArn
  - name: eks-cluster-name
    valueFrom:
      moduleMetadata:
        group: compute
        name: eks
        key: EksClusterName
  - name: eks-oidc-arn
    valueFrom:
      moduleMetadata:
        group: compute
        name: eks
        key: EksOidcArn
  - name: eks-openid-issuer
    valueFrom:
      moduleMetadata:
        group: compute
        name: eks
        key: EksClusterOpenIdConnectIssuer
  - name: eks-handler-rolearn
    valueFrom:
      moduleMetadata:
        group: compute
        name: eks
        key: EksHandlerRoleArn
  - name: emr-eks-namespace
    value: emr-eks-spark
  - name: logs-bucket-name
    valueFrom:
      moduleMetadata:
        group: storage
        name: buckets
        key: LogsBucketName
  - name: artifacts-bucket-name
    valueFrom:
      moduleMetadata:
        group: storage
        name: buckets
        key: ArtifactsBucketName
```

### Module Metadata Outputs

- `EmrJobExecutionRoleArn`: ARN for the EMR On EKS Execution Role
- `VirtualClusterId`: Cluster ID for the EMR Virtual Cluster ID

#### Output Example

EksRbacStack:

```json
{
    "EmrJobExecutionRoleArn":"arn:aws:iam::1234567890:role/addf-demo-simulations-emr-XXXXXXXX"
}
```

EMRStack:

```json
{
    "VirtualClusterId":"ncXXXXXXXX"
}
