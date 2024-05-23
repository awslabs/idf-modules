# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List, cast

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_opensearchservice as opensearch
import cdk_nag
from aws_cdk import Aspects, RemovalPolicy, Stack, Tags
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class OpenSearchStack(Stack):  # type: ignore
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
        os_domain_retention: str,
        os_data_nodes: int,
        os_data_node_instance_type: str,
        os_master_nodes: int,
        os_master_node_instance_type: str,
        os_ebs_volume_size: int,
        stack_description: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, description=stack_description, **kwargs)

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

        os_access_policy = {
            "Effect": "Allow",
            "Action": "es:*",
            "Principal": {"AWS": "*"},
            "Resource": "*",
        }

        # Create SecurityGroup for OpenSearch
        os_security_group = cast(
            ec2.ISecurityGroup, ec2.SecurityGroup(self, f"{dep_mod}-sg", vpc=self.vpc, allow_all_outbound=True)
        )

        # The capacity in Nodes and Volume Size/Type for the AWS OpenSearch
        os_capacity = opensearch.CapacityConfig(
            data_nodes=os_data_nodes,
            data_node_instance_type=os_data_node_instance_type,
            master_nodes=os_master_nodes,
            master_node_instance_type=os_master_node_instance_type,
        )

        os_ebs = opensearch.EbsOptions(
            enabled=True,
            volume_type=ec2.EbsDeviceVolumeType.GP2,
            volume_size=os_ebs_volume_size,
        )

        # Note that this AWS OpenSearch domain is optimised for
        # cost rather than availability and defaults to one node
        # in a single availability zone
        self.private_subnets = []
        for idx, subnet_id in enumerate(private_subnet_ids):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(scope=self, id=f"subnet{idx}", subnet_id=subnet_id))

        os_domain = opensearch.Domain(
            self,
            "OSDomain",
            removal_policy=RemovalPolicy.RETAIN if os_domain_retention.upper() == "RETAIN" else RemovalPolicy.DESTROY,
            # https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-opensearchservice.EngineVersion.html
            version=opensearch.EngineVersion.OPENSEARCH_1_0,
            vpc=self.vpc,
            vpc_subnets=[ec2.SubnetSelection(subnets=[self.private_subnets[0]])],
            security_groups=[os_security_group],
            capacity=os_capacity,
            ebs=os_ebs,
            access_policies=[iam.PolicyStatement.from_json(os_access_policy)],
            domain_name=dep_mod,
            enforce_https=True,
            node_to_node_encryption=True,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
            tls_security_policy=opensearch.TLSSecurityPolicy.TLS_1_2,
            logging=opensearch.LoggingOptions(
                slow_search_log_enabled=True, app_log_enabled=True, slow_index_log_enabled=True
            ),
        )

        url = f"https://{os_domain.domain_endpoint}/_dashboards/"
        self.domain_endpoint = os_domain.domain_endpoint
        self.domain_name = os_domain.domain_name
        self.dashboard_url = url
        self.os_sg_id = os_security_group.security_group_id

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
