# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, List, Optional, cast

import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_eks as eks
from aws_cdk import aws_iam as iam
from aws_cdk.lambda_layer_kubectl_v29 import KubectlV29Layer
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct


class FSXFileStorageOnEKS(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        fsx_dns_name: str,
        fsx_mount_name: str,
        fsx_file_system_id: str,
        fsx_security_group_id: str,
        fsx_storage_capacity: str,
        eks_namespace: str,
        eks_cluster_name: str,
        eks_admin_role_arn: str,
        eks_oidc_arn: str,
        eks_handler_role_arn: str,
        eks_cluster_security_group_id: str,
        dra_export_path: str,
        vpc_id: Optional[str],
        private_subnet_ids: Optional[List[str]],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            scope,
            id,
            description="This stack connects an existing FSX-Lustre to an existing EKS",
            **kwargs,
        )

        self.project_name = project_name
        self.deployment_name = deployment_name
        self.module_name = module_name
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=f"{self.project_name}-{self.deployment_name}")

        dep_mod = f"{self.project_name}-{self.deployment_name}-{self.module_name}"
        dep_mod = dep_mod[:30]

        # Import EKS Cluster
        provider = eks.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self, f"{dep_mod}-provider", eks_oidc_arn
        )

        handler_role = iam.Role.from_role_arn(self, "HandlerRole", eks_handler_role_arn)

        # Required if EKS cluster endpoint is not accessible publicly
        vpcConfig = (
            {
                "vpc": ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id),
                "kubectl_private_subnet_ids": private_subnet_ids,
                "kubectl_security_group_id": eks_cluster_security_group_id,
            }
            if vpc_id
            else {}
        )

        eks_cluster = eks.Cluster.from_cluster_attributes(
            self,
            f"{dep_mod}-eks-cluster",
            cluster_name=eks_cluster_name,
            kubectl_role_arn=eks_admin_role_arn,
            open_id_connect_provider=provider,
            kubectl_lambda_role=handler_role,
            kubectl_layer=KubectlV29Layer(self, "Kubectlv29Layer"),
            **vpcConfig,  # type: ignore
        )

        fsx_security_group = ec2.SecurityGroup.from_security_group_id(self, "FSXSecurityGroup", fsx_security_group_id)
        eks_security_group = ec2.SecurityGroup.from_security_group_id(
            self, "EKSSecurityGroup", eks_cluster_security_group_id
        )
        fsx_security_group.connections.allow_from(
            eks_security_group,
            ec2.Port.tcp(988),
            "allowtraffic from EKS nodes",
        )

        fsx_security_group.connections.allow_from(
            eks_security_group,
            ec2.Port.tcp(1021),
            "allowtraffic from EKS nodes",
        )

        fsx_security_group.connections.allow_from(
            eks_security_group,
            ec2.Port.tcp(1022),
            "allowtraffic from EKS nodes",
        )

        fsx_security_group.connections.allow_from(
            eks_security_group,
            ec2.Port.tcp(1023),
            "allowtraffic from EKS nodes",
        )

        self.storage_class_name = f"{module_name}-fsx-sc"
        self.pv_name = f"{module_name}-fsx-pv"
        self.pvc_name = f"{module_name}-fsx-pvc"

        namespace_manifest = eks.KubernetesManifest(
            self,
            "namespace",
            cluster=eks_cluster,
            manifest=[
                {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": eks_namespace},  # Create if not exist
                }
            ],
            overwrite=True,
        )

        # Static Provisioning for FSX

        # Creates a PV
        persistent_volume_manifest = eks_cluster.add_manifest(
            "FSXCSIPersistentVolume",
            {
                "apiVersion": "v1",
                "kind": "PersistentVolume",
                "metadata": {"name": self.pv_name},
                "spec": {
                    "capacity": {"storage": fsx_storage_capacity},
                    "volumeMode": "Filesystem",
                    "accessModes": ["ReadWriteMany"],
                    "mountOptions": ["flock"],
                    "persistentVolumeReclaimPolicy": "Recycle",
                    "csi": {
                        "driver": "fsx.csi.aws.com",
                        "volumeHandle": fsx_file_system_id,
                        "volumeAttributes": {
                            "dnsname": fsx_dns_name,
                            "mountname": fsx_mount_name,
                        },
                    },
                },
            },
        )

        persistent_volume_manifest.node.add_dependency(namespace_manifest)

        # Creates a PVC
        pvc_manifest = eks_cluster.add_manifest(
            "FSXCSIPersistentVolumeClaim",
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {"name": self.pvc_name, "namespace": eks_namespace},
                "spec": {
                    "accessModes": ["ReadWriteMany"],
                    "resources": {"requests": {"storage": "1200Gi"}},
                    "storageClassName": "",
                    "volumeMode": "Filesystem",
                    "volumeName": self.pv_name,
                },
            },
        )

        pvc_manifest.node.add_dependency(namespace_manifest)

        # Add a job that will change the permissions on FSx so that users w/o sudo can write to it
        job_manifest = eks_cluster.add_manifest(
            "SetPermissionsJob",
            {
                "apiVersion": "batch/v1",
                "kind": "Job",
                "metadata": {"name": "set-permissions-job", "namespace": eks_namespace},
                "spec": {
                    "ttlSecondsAfterFinished": 60,
                    "template": {
                        "spec": {
                            "restartPolicy": "Never",
                            "containers": [
                                {
                                    "name": "set-permissions-job",
                                    "image": "public.ecr.aws/amazonlinux/amazonlinux:2",
                                    "command": ["/bin/sh", "-c"],
                                    "args": [
                                        f"chmod -R 777 {dra_export_path}",
                                        f"chown -R root:users {dra_export_path}",
                                    ],
                                    "volumeMounts": [
                                        {
                                            "name": "persistent-storage",
                                            "mountPath": dra_export_path,
                                            "subPath": dra_export_path[1:],
                                        }
                                    ],
                                }
                            ],
                            "volumes": [
                                {
                                    "name": "persistent-storage",
                                    "persistentVolumeClaim": {"claimName": self.pvc_name},
                                }
                            ],
                        },
                    },
                },
            },
        )

        job_manifest.node.add_dependency(namespace_manifest)
        job_manifest.node.add_dependency(persistent_volume_manifest)
        job_manifest.node.add_dependency(pvc_manifest)

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        NagSuppressions.add_stack_suppressions(
            self,
            apply_to_nested_stacks=True,
            suppressions=[
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM4",
                        "reason": "Managed Policies are for service account roles only",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM5",
                        "reason": "Resource access restriced to ADDF resources",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-L1",
                        "reason": "Suppress error caused by python_3_12 release in December",
                    }
                ),
            ],
        )
