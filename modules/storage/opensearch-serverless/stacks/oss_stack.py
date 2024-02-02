# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any, List, cast

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_opensearchserverless as opensearch_s
import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class OpenSearchServerlessStack(Stack):  # type: ignore
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        deployment_name: str,
        module_name: str,
        hash: str,
        vpc_id: str,
        private_subnet_ids: List[str],
        vpc_endpoint_id: str,
        oss_cluster_sg_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, description="This stack creates Amazon Opensearch cluster resources", **kwargs)

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"

        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        """
        dep_mod is used to name OpenSearch domain and the max length cant exceed 28 character
        https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html
        """
        dep_mod = dep_mod[:19] + "-" + hash
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        # ###  OpenSearch Starts Here!!
        self.vpc_id = vpc_id
        self.vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=vpc_id,
        )

        self.private_subnets = []
        for idx, subnet_id in enumerate(private_subnet_ids):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(scope=self, id=f"subnet{idx}", subnet_id=subnet_id))

        collection_name = dep_mod

        network_security_policy = json.dumps(
            [
                {
                    "Rules": [
                        {"Resource": [f"collection/{collection_name}"], "ResourceType": "dashboard"},
                        {"Resource": [f"collection/{collection_name}"], "ResourceType": "collection"},
                    ],
                    "AllowFromPublic": False,
                    "SourceVPCEs": [vpc_endpoint_id],
                }
            ],
            indent=2,
        )

        # max length of Network policy name is 32
        network_security_policy_name = f"{collection_name}-np"
        assert len(network_security_policy_name) <= 32

        cfn_network_security_policy = opensearch_s.CfnSecurityPolicy(
            self,
            "NetworkSecurityPolicy",
            policy=network_security_policy,
            name=network_security_policy_name,
            type="network",
        )

        encryption_security_policy = json.dumps(
            {
                "Rules": [{"Resource": [f"collection/{collection_name}"], "ResourceType": "collection"}],
                "AWSOwnedKey": True,
            },
            indent=2,
        )

        # max length of Encryption policy name is 32
        encryption_security_policy_name = f"{collection_name}-ep"
        assert len(encryption_security_policy_name) <= 32

        cfn_encryption_security_policy = opensearch_s.CfnSecurityPolicy(
            self,
            "OSSEncryptionSecurityPolicy",
            policy=encryption_security_policy,
            name=encryption_security_policy_name,
            type="encryption",
        )

        self.cfn_collection = opensearch_s.CfnCollection(
            self,
            "OSSCollection",
            name=collection_name,
            description="Collection to be used for time-series analysis using OpenSearch Serverless",
            type="SEARCH",  # [VECTORSEARCH, TIMESERIES]
        )
        self.cfn_collection.add_dependency(cfn_network_security_policy)
        self.cfn_collection.add_dependency(cfn_encryption_security_policy)

        collection_pipeline_policy_doc = iam.PolicyDocument()

        collection_pipeline_policy_doc.add_statements(
            iam.PolicyStatement(
                **{
                    "effect": iam.Effect.ALLOW,
                    "resources": ["*"],
                    "actions": ["aoss:BatchGetCollection"],
                }  # type: ignore
            )
        )

        pipeline_role = iam.Role(
            self,
            "OSSIngestionPipelineRole",
            role_name=f"{dep_mod}-OSSCollePipelineRole",
            assumed_by=iam.ServicePrincipal("osis-pipelines.amazonaws.com"),
            inline_policies={"collection-pipeline-policy": collection_pipeline_policy_doc},
        )
        self.iam_role = pipeline_role

        data_access_policy = json.dumps(
            [
                {
                    "Rules": [
                        {
                            "Resource": [f"collection/{collection_name}"],
                            "Permission": [
                                "aoss:CreateCollectionItems",
                                "aoss:DeleteCollectionItems",
                                "aoss:UpdateCollectionItems",
                                "aoss:DescribeCollectionItems",
                            ],
                            "ResourceType": "collection",
                        },
                        {
                            "Resource": [f"index/{collection_name}/*"],
                            "Permission": [
                                "aoss:CreateIndex",
                                "aoss:DeleteIndex",
                                "aoss:UpdateIndex",
                                "aoss:DescribeIndex",
                                "aoss:ReadDocument",
                                "aoss:WriteDocument",
                            ],
                            "ResourceType": "index",
                        },
                    ],
                    "Principal": [f"{self.iam_role.role_arn}"],
                    "Description": "data-access-rule",
                }
            ],
            indent=2,
        )

        # max length of Access Policy name is 32
        data_access_policy_name = f"{collection_name}-ap"
        assert len(data_access_policy_name) <= 32

        opensearch_s.CfnAccessPolicy(
            self,
            "OpssDataAccessPolicy",
            name=data_access_policy_name,
            description="Policy for data access",
            policy=data_access_policy,
            type="data",
        )

        self.oss_cluster_sg_id = oss_cluster_sg_id

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        NagSuppressions.add_stack_suppressions(
            self,
            [
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS2",
                        "reason": "Node to Node encryption not enabled - no customer data",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS3",
                        "reason": "Access restricted by security group ingress permissions in VPC",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS4",
                        "reason": "Single noe for demo purposes",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS5",
                        "reason": "Access restricted by security group ingress permissions in VPC",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS7",
                        "reason": "Single Node for Demo purposes",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS8",
                        "reason": "No customer data - for Demo purposes",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-OS9",
                        "reason": "No logs - for Demo purposes",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM4",
                        "reason": "Managed policies used by service accout roles and managed service",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM5",
                        "reason": "Policies applied for Custom Resources",
                    }
                ),
            ],
        )
