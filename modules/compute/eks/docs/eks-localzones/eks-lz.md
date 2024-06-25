# EKS Cluster in Local Zones

## Description

Suitable for Latency sensitive workloads or workloads that needs to meet extensive security requirements. For more info, checkout [here](https://docs.aws.amazon.com/local-zones/latest/ug/what-is-aws-local-zones.html)

When you deploy AWS EKS in Local Zones, the Control plane will be launched in parent region and the Data plane will be launched in [Local Zone Subnets](https://docs.aws.amazon.com/eks/latest/userguide/local-zones.html)

### Deployment

You can deploy the networking module available at `modules/network/basic-cdk` , with the below settings to deploy networking with LocalZone enabled:

```yaml
name: basic-networking
path: modules/network/basic-cdk/
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
  - name: local-zones
    value: 
      - eu-central-1-ham-1a
```

> Note: You need to enable LocalZones primarily and then declare the enabled subnet(s) as value(s) to `local-zones` parameter (declared above)

You can deploy the below sample declaration of EKS module manifest

```yaml
name: eks
path: modules/core/eks/
dataFiles:
  - filePath: data/eks_dockerimage-replication/versions/<<EKS_VERSION>>.yaml #replace the EKS_VERSION with the right EKS Cluster version
  - filePath: data/eks_dockerimage-replication/versions/default.yaml
parameters:
  - name: vpc-id
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: VpcId
  - name: controlplane-subnet-ids
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: PrivateSubnetIds
  - name: dataplane-subnet-ids
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: LocalZonePrivateSubnetIds
  - name: eks-admin-role-name
    value: Admin
  - name: eks-poweruser-role-name
    value: PowerUser
  - name: eks-read-only-role-name
    value: ReadOnly
  - name: eks-version
    value: 1.29 # Replace the EKS_VERSION inline here or set an env var and load it from `.env` file using below format
    # valueFrom:
    #   envVariable: GLOBAL_EKS_VERSION
  - name: eks-compute
    value:
      eks_nodegroup_config:
        - eks_ng_name: ng1
          eks_node_quantity: 1
          eks_node_max_quantity: 5
          eks_node_min_quantity: 1
          eks_node_disk_size: 20
          eks_node_instance_type: "m5.2xlarge"
          eks_self_managed: True
      eks_node_spot: False
      eks_api_endpoint_private: False # This makes the EKS Endpoint public
      eks_secrets_envelope_encryption: True 
  - name: eks-addons
    value:
      deploy_aws_lb_controller: True
      # Storage
      deploy_aws_ebs_csi: True 
      deploy_aws_s3_csi: True
      deploy_aws_fsx_csi: True
      # Autoscaling
      deploy_cluster_autoscaler: True 
      deploy_metrics_server: True 
      # Secrets
      deploy_secretsmanager_csi: True 
      # Monitoring/Logging/Tracing
      deploy_cloudwatch_observability_addon: True
```

#### FAQs

- What are the instance types supported in LocalZones?

You can checkout the region of interest [here](https://aws.amazon.com/about-aws/global-infrastructure/localzones/features/), which documents the compatible instance type with EBS option(s)

- Can i deploy both Managed and Self managed node groups to the EKS Cluster?

Unfortunately you cannot deploy Managed node groups to Local Zones yet. The only option is to deploy Self managed node groups.