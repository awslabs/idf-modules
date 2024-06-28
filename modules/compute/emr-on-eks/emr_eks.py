# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, cast

import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from aws_cdk import aws_emrcontainers as emrc
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct


class EmrEksStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        eks_cluster_name: str,
        emr_eks_namespace: str,
        **kwargs: Any,
    ) -> None:
        # Project Env vars
        self.project_name = project_name
        self.deployment_name = deployment_name
        self.module_name = module_name
        self.emr_eks_namespace = emr_eks_namespace

        dep_mod = f"{self.project_name}-{self.deployment_name}-{self.module_name}"
        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod

        super().__init__(
            scope,
            id,
            description="This stack deploys a Virtual Cluster for deploying Spark jobs using EMR on EKS",
            **kwargs,
        )

        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        # EMR virtual cluster
        self.emr_vc = emrc.CfnVirtualCluster(
            scope=self,
            id=f"{full_dep_mod}-EMRVirtualCluster",
            container_provider=emrc.CfnVirtualCluster.ContainerProviderProperty(
                id=eks_cluster_name,
                info=emrc.CfnVirtualCluster.ContainerInfoProperty(
                    eks_info=emrc.CfnVirtualCluster.EksInfoProperty(namespace=self.emr_eks_namespace)
                ),
                type="EKS",
            ),
            name=f"{full_dep_mod}-EMROnEKSCluster",
        )

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
                        "reason": "Resource access restriced to IDF resources",
                    }
                ),
            ],
        )
