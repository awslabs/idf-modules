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

You can deploy the sample manifest `eks-lz-manifest.yaml` available in the same folder relative to this doc

#### FAQs

- What are the instance types supported in LocalZones?

You can checkout the region of interest [here](https://aws.amazon.com/about-aws/global-infrastructure/localzones/features/), which documents the compatible instance type with EBS option(s)

- Can i deploy both Managed and Self managed node groups to the EKS Cluster?

Unfortunately you cannot deploy Managed node groups to Local Zones yet. The only option is to deploy Self managed node groups.