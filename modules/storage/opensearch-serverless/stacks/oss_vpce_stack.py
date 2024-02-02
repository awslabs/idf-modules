# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, cast

import aws_cdk as cdk
from aws_cdk import Stack, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_opensearchserverless as opensearch_s
from constructs import Construct, IConstruct


class OpenSearchServerlessVpcEndpointStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc_id: str,
        private_subnet_ids: List[str],
        project_name: str,
        deployment_name: str,
        module_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"
        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        """
        dep_mod is used to name OpenSearch domain and the max length cant exceed 28 character
        https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html
        """
        dep_mod = dep_mod[:19]
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        self.vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=vpc_id,
        )

        oss_cluster_sg = ec2.SecurityGroup(
            self,
            "OSSSG",
            vpc=self.vpc,
            allow_all_outbound=True,
            description="security group for an opensearch serverless cluster",
            security_group_name=f"{dep_mod}-oss-cluster-sg",
        )

        cfn_oss_vpc_endpoint = opensearch_s.CfnVpcEndpoint(
            self,
            "OSSVpcEndpoint",
            name=f"{dep_mod}-oss-vpce",  # Expected maxLength: 32
            vpc_id=vpc_id,
            security_group_ids=[oss_cluster_sg.security_group_id],
            subnet_ids=private_subnet_ids,
        )

        cfn_oss_vpc_endpoint.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        self.vpc_endpoint_id = cfn_oss_vpc_endpoint.ref
        self.oss_cluster_sg_id = oss_cluster_sg.security_group_id
