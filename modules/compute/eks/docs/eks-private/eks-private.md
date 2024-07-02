# EKS Cluster in Private Subnets

### Sample declaration of EKS module manifest

#### When deployed EKS Control plane and Data plane standalone in Private Subnets

Refer to `eks-private-manifest.yaml` available in the folder relative to this document

#### If you want to launch app pods in the extended VPC CIDR, follow the below manifest

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
        key: PrivateSubnetIds
  - name: custom-subnet-ids # Make sure to extend VPC CIDR before you launch EKS cluster and substitute the extended subnet IDS below
    value: ["subnet-XXXXXXXXX", "subnet-XXXXXXXXX"]
```

> Note: Add the rest of nodegroup and addons config as per requirement