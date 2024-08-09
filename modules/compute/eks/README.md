# EKS

## Description

This module creates an EKS Cluster with the following features and addons available for use:

- Can create EKS Control plane and data plane in Private Subnets (having NATG in the route tables)
- Can create EKS Control plane in Private Subnets and data plane in Isolated Subnets (having Link local route in the route tables)
- Can launch application pods in secondary CIDR to save IP exhaustion in the primary CIDR
- Encrypts the root EBS volumes of managed node groups
- Can encrypt the EKS Control plane using Envelope encryption

### Plugins supported by category

Load balancing:

- ALB Ingress Controller - recommended
- Nginx Ingress Controller

> Note: Haven't tested in china region

Storage:

- EBS CSI Driver
- EFS CSI Driver

> Note: Not supported in china region, because the container image needs to be pulled from ECR Public registry which is blocked by china firewall

- S3 CSI Driver

> Note: Not supported in china region, because IDF EKS module uses EKS Addon to deploy it. To support it, user can deploy helm chart

- FSX Lustre Driver

> Note: Haven't tested in China region

Secrets:

- Secrets Manager CSI Driver

> Note: Not supported in china region, because the container image needs to be pulled from ECR Public registry which is blocked by china firewall

Scaling:

- Horizontal Pod Autoscaler (HPA) - recommended

> Note: Not supported in china region, because the container image needs to be pulled from ECR Public registry which is blocked by china firewall

- Cluster Autoscaler (CA) - recommended

> Note: Not supported in china region, because the container image needs to be pulled from ECR Public registry which is blocked by china firewall

Monitoring/Logging/Alerting:

- Cloudwatch Container Insights (logs)

> Note: Haven't tested in China region

- Amazon CloudWatch Observability EKS add-on (deploys metrics and logging drivers using EKS Managed Addon) - recommended

- Amazon EKS add-on support for ADOT Operator

> Note: Haven't tested in China region

Networking:

- Custom CIDR implementation

> Note: Haven't tested in China region

- Calico for network isolation/security

> Note: Haven't tested in China region

Security:

- Kyverno policies (policy as enforcement in k8s)

> Note: Haven't tested in China region

## Explaining the attributes

### Input Paramenters

#### Required

- `dataFiles`: Data files is a [seedfarmer feature](https://seed-farmer.readthedocs.io/en/latest/manifests.html#a-word-about-datafiles) which helps you to link a commonly available directory at the root of the repo. For EKS module, we declare the list of helm chart versions inside the supported `k8s-version.yaml` with the detailed metadata available inside the `default.yaml` for every supported plugin.
- `vpc-id`: The VPC-ID that the cluster will be created in
- `controlplane-subnet-ids`: The controlplane subnets that the EKS Cluster should be deployed in. These subnets should have internet connectivity enabled via NATG
- `dataplane-subnet-ids`: The dataplane subnets can be either private subnets (NATG enabled) or in isolated subnets(link local route only) depending on the compliance required to achieve
- `eks-compute` and `eks_nodegroup_config`: List of EKS Managed NodeGroup Configurations to use with the preferred EC2 instance types. The framework would automatically encrypt the root volume
  - `eks_nodegroup_config` allows list of nodegroups to be deployed. Following are the supported attributes:

    ```yaml
          eks_ng_name: Declare the Node group name here
          eks_node_quantity: Declare the Node group desired size here
          eks_node_max_quantity: Declare the Node group maximum size here
          eks_node_min_quantity: Declare the Node group minimum size here
          eks_node_disk_size: Declare the Node group EBS volume disk size here
          eks_node_instance_type: Declare the Node group desired instance type here
          eks_node_labels: Declare the Kubernetes labels here, so they will be propogated to the nodes
          eks_node_taints: Declare the Kubernetes taints here, so they will be propogated to the nodes. Pods should tolerate these taints for being able to schedule workloads on them
          use_gpu_ami: Enable if you want to deploy GPU instances in the node group
          install_nvidia_device_plugin: Install [Nvidia Device plugin](https://github.com/NVIDIA/k8s-device-plugin) for management of available GPU resources on a node. You would need to use an AMI with GPU drivers, container runtime already configured. It is recommended to use AWS GPU Optimized AMI, which is done for you if you set the attribute `use_gpu_ami` above. Checkout the [example](https://github.com/NVIDIA/k8s-device-plugin?tab=readme-ov-file#running-gpu-jobs) here on how to request GPUs from the pod spec.
          
      ```

- `eks-version`: The EKS Cluster version to lock the version to
- `eks-addons`: List of EKS addons to deploy on the EKS Cluster

#### Optional

- `mountpoint-buckets`: An optional list of bucket(s) that you want to mount with your application. IAM Permissions to the bucket(s) will be configured by the EKS module.
- `custom-subnet-ids`: The custom subnets for assigning IP addresses to the pods. Usually used when there is a limited number of IP addresses available in the primary CIDR subnets. Refer to [custom networking](https://docs.aws.amazon.com/eks/latest/userguide/cni-custom-network.html) for feature details 
- `eks_admin_role_name`: The Admin Role to be mapped to the `systems:masters` group of RBAC
- `eks_poweruser_role_name`: The PowerUser Role to be mapped to the `poweruser-group` group of RBAC
- `eks_readonly_role_name`: The ReadOnly Role to be mapped to the `readonly-group` group of RBAC
- `eks_node_spot`: If `eks_node_spot` is set to True, we deploy SPOT instances of the above `nodegroup_config` for you else we deploy `ON_DEMAND` instances.
- `eks_secrets_envelope_encryption`: If set to True, we enable KMS secret for [envelope encryption](https://aws.amazon.com/about-aws/whats-new/2020/03/amazon-eks-adds-envelope-encryption-for-secrets-with-aws-kms/) for Kubernetes secrets.
- `eks_api_endpoint_private`: If set to `True`, we deploy the EKS cluster with API endpoint set to [private mode](https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html). By default, it is set to `PUBLIC AND PRIVATE` access mode (which whitelists `0.0.0.0/0` CIDR). If you want to whitelist custom CIDRs instead of the default whitelisted CIDR, you can either set `ips_to_whitelist_from_ssm` or `ips_to_whitelist_adhoc` attribute(s). You should not set either of them if `eks_api_endpoint_private` is set to `True`.
- `ips_to_whitelist_from_ssm`: You can load a list of SSM Parameters in which your enterprise stores CIDRs to be whietlisted. The SSM Parameters should be declared in a `.env` file (feature supported by SeedFarmer). If you set this parameter, the EKS module also loads the list of CODEBUILD Public IPS from `ip-ranges.json` [file](https://ip-ranges.amazonaws.com/ip-ranges.json) based on the region of operation, so your seedfarmer commands continue to work. Below is an example declaration:

```yaml
eks_api_endpoint_private: False
ips_to_whitelist_from_ssm: ${IPS_TO_WHITELIST_FROM_SSM}
```

```.env
IPS_TO_WHITELIST_FROM_SSM=["/company/org/ip-whitelists1", "/company/org/ip-whitelists2"]
```

- `ips_to_whitelist_adhoc`: You can declare a list of Public CIDRs which needs to be whietlisted. The entities leveraging Public CIDRs can be declared in a `.env` file (feature supported by SeedFarmer). If you set this parameter, the EKS module also loads the list of CODEBUILD Public IPS from `ip-ranges.json` [file](https://ip-ranges.amazonaws.com/ip-ranges.json) based on the region of operation, so your seedfarmer commands continue to work. Below is an example declaration:

```yaml
eks_api_endpoint_private: False
ips_to_whitelist_adhoc: ${IPS_TO_WHITELIST_ADHOC}
```

```.env
IPS_TO_WHITELIST_ADHOC=["1.2.3.4/8", "11.2.33.44/8"]
```

#### Optional Drivers/Addons/Plugins

- `deploy_aws_lb_controller`: Deploys the [ALB Ingress controller](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html). Default behavior is set to False
- `deploy_external_dns`: Deploys the External DNS to interact with [AWS Route53](https://github.com/kubernetes-sigs/external-dns/blob/master/docs/tutorials/aws.md). Default behavior is set to False
- `deploy_aws_ebs_csi`: Deploys the [AWS EBS](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) Driver. Default behavior is set to False
- `deploy_aws_efs_csi`: Deploys the [AWS EFS](https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html). Default behavior is set to False
- `deploy_aws_fsx_csi`: Deploys the [AWS FSX](https://docs.aws.amazon.com/eks/latest/userguide/fsx-csi.html). Default behavior is set to False
- `deploy_aws_s3_csi`: Deploys the [Amazon S3](https://docs.aws.amazon.com/eks/latest/userguide/s3-csi.html). Default behavior is set to False
- `deploy_cluster_autoscaler`: Deploys the [Cluster Autoscaler](https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html) to scale EKS Workers
- `deploy_metrics_server`: Deploys the [Metrics server](https://docs.aws.amazon.com/eks/latest/userguide/metrics-server.html) and HPA for scaling out/in pods. Default behavior is set to False
- `deploy_secretsmanager_csi`: Deploys [Secrets Manager CSI driver](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html) to interact with Secrets mounted as files. Default behavior is set to False
- `deploy_cloudwatch_container_insights_metrics`: Deploys the [CloudWatch Agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-EKS-agent.html) to ingest containers metrics into AWS Cloudwatch. Default behavior is set to False
- `deploy_cloudwatch_container_insights_logs`: Deploys the [Fluent bit](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-logs-FluentBit.html) plugin to ingest containers logs into AWS Cloudwatch. Default behavior is set to False
- `deploy_adot`: Deploys AWS Distro for OpenTelemetry (ADOT) which is a secure, production-ready, AWS supported distribution of the OpenTelemetry project.
- `deploy_amp`: Deploys AWS Managed Prometheus for centralized log monitoring - ELK Stack. Default behavior is set to False
- `deploy_grafana_for_amp`: Deploys Grafana boards for visualization of logs/metrics from Elasticsearch/Opensearch cluster. Default behavior is set to False
- `deploy_kured`: Deploys [kured reboot daemon](https://github.com/kubereboot/kured) that performs safe automatic node reboots when the need to do so is indicated by the package management system of the underlying OS. Default behavior is set to False
- `deploy_calico`: Deploys [Calico network engine](https://docs.aws.amazon.com/eks/latest/userguide/calico.html) and default-deny network policies. Default behavior is set to False.
- `deploy_nginx_controller`: Deploys [nginx ingress controller](https://aws.amazon.com/blogs/opensource/network-load-balancer-nginx-ingress-controller-eks/). You can provide `nginx_additional_annotations` which populates Optional list of nginx annotations. Default behavior is set to False
- `deploy_kyverno`: Deploys [Kyverno policy engine](https://aws.amazon.com/blogs/containers/managing-pod-security-on-amazon-eks-with-kyverno/) which is is a Policy-as-Code (PaC) solution that includes a policy engine designed for Kubernetes. You can provide the list of policies to be enabled using `kyverno_policies` attribute. Default behavior is set to False

### How to launch EKS Cluster in [Private Subnets](./docs/eks-private/eks-private.md)

### How to launch EKS Cluster in [Isolated Subnets](./docs/eks-isolated/eks-isolated.md)

### How to launch EKS Cluster in [Local Zones](./docs/eks-localzones/eks-lz.md)

#### IAM integration

EKS integrates with AWS Identity and Access Management (IAM) to control access to Kubernetes resources. IAM policies can be used to control access to Kubernetes API server and resources. EKS also supports role-based access control (RBAC), which allows you to define fine-grained access controls for users and groups. As of now we defined three roles, more roles can be added and refined as the requirements:

1. Admin role - allows full access to the namespaced and cluster-wide resources of EKS
2. Poweruser role - allows CRUD operations for namespaced resources of the EKS cluster
3. Read-only role - allows read operations for namespaced resources of the EKS cluster

#### Logging & Monitoring

- It is recommended to deploy [Amazon CloudWatch Observability EKS add-on](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-EKS-addon.html) which helps collecting infrastructure metrics using CloudWatch agent, helps sending container logs using Fluent Bit and the target is AWS CloudWatch.

> Note: The EKS module supports the list of monitoring solutions declared in the beginning of the doc.

### Module Metadata Outputs

- `EksClusterName`: The EKS Cluster Name
- `EksClusterAdminRoleArn`: The EKS Cluster's Admin Role Arn
- `EksClusterSecurityGroupId`: The EKS Cluster's SecurityGroup ID
- `EksOidcArn`: The EKS Cluster's OIDC Arn
- `EksClusterOpenIdConnectIssuer`: EKS Cluster's OPEN ID Issuer
- `EksClusterMasterRoleArn` - the masterrole used for cluster creation
- `EksNodeRoleArn` - the role assigned to nodes when nodes are spinning up in node groups.

#### Output Example

```json
{
  "EksClusterName": "idf-local-core-eks-cluster",
  "EksClusterAdminRoleArn": "arn:aws:iam::XXXXXXXX:role/idf-local-core-eks-stack-clusterCreationRoleXXXX",
  "EksClusterSecurityGroupId": "sg-XXXXXXXXXXXXXX",
  "EksOidcArn": "arn:aws:iam::XXXXXXXX:oidc-provider/oidc.eks.us-west-2.amazonaws.com/id/XXXXXXXX",
  "EksClusterOpenIdConnectIssuer": "oidc.eks.us-west-2.amazonaws.com/id/098FBE7B04A9C399E4A3534FF1C288C6",
  "EksClusterMasterRoleArn": "arn:aws:iam::XXXXXXXX:role/idf-local-core-eks-us-east-1-masterrole",
  "EksHandlerRoleArn": "arn:aws:iam::XXXXXXXX:role/idf-clusterKubectlHandlerRole",
  "EksNodeRoleArn": "arn:aws:iam::XXXXXXXX:role/idf-local-core-eks-us-east-1-noderole"
}

```
