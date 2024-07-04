# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List, cast

import aws_cdk.aws_ec2 as ec2
import cdk_nag
from aws_cdk import Aspects, Duration, RemovalPolicy, Stack, Tags
from aws_cdk import aws_neptune_alpha as neptune  # type: ignore
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class NeptuneStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        deployment_name: str,
        module_name: str,
        vpc_id: str,
        private_subnet_ids: List[str],
        number_instances: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, description="This stack deploys Amazon Neptune Cluster resources", **kwargs)

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"

        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        """
        dep_mod is used to name Neptune cluster and the max length cant exceed 64 characters
        https://docs.aws.amazon.com/neptune/latest/apiref/API_CreateDBCluster.html
        """
        dep_mod = dep_mod[:27]
        # Tagging all resources
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        # Importing the VPC
        self.vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=vpc_id,
        )

        self.private_subnets = []
        for idx, subnet_id in enumerate(private_subnet_ids):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(scope=self, id=f"subnet{idx}", subnet_id=subnet_id))

        sg_graph_db = ec2.SecurityGroup(
            self,
            f"{dep_mod}NeptuneSG",
            vpc=self.vpc,
            allow_all_outbound=True,
            description=f"{dep_mod} Security Group for Cluster",
            security_group_name=f"{dep_mod}-sg",
        )

        sg_graph_db.add_ingress_rule(peer=sg_graph_db, connection=ec2.Port.tcp(8182), description="Neptune Ingress")

        sg_graph_db.connections.allow_from(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8182),
            "allow HTTPS traffic from anywhere",
        )

        cluster_params = neptune.ClusterParameterGroup(
            self,
            f"{dep_mod}ClusterParams",
            description="Cluster parameter group",
            family=neptune.ParameterGroupFamily.NEPTUNE_1_3,
            parameters={"neptune_enable_audit_log": "1"},
        )

        db_params = neptune.ParameterGroup(
            self,
            "DbParams",
            description="Db parameter group",
            family=neptune.ParameterGroupFamily.NEPTUNE_1_3,
            parameters={"neptune_query_timeout": "120000"},
        )

        subnet_group = neptune.SubnetGroup(
            self,
            f"{dep_mod}SubnetGroup",
            vpc=self.vpc,
            description="Some Description",
            removal_policy=RemovalPolicy.DESTROY,
            vpc_subnets=ec2.SubnetSelection(subnets=self.private_subnets),
        )

        cluster = neptune.DatabaseCluster(
            self,
            f"{dep_mod}DBCluster",
            vpc=self.vpc,
            db_cluster_name=f"{dep_mod}Cluster",
            instance_type=neptune.InstanceType.R5_LARGE,
            backup_retention=Duration.days(7),
            cluster_parameter_group=cluster_params,
            parameter_group=db_params,
            instances=number_instances,
            subnet_group=subnet_group,
            preferred_backup_window="08:45-09:15",
            preferred_maintenance_window="sun:18:00-sun:18:30",
            auto_minor_version_upgrade=True,
            security_groups=[sg_graph_db],
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.cluster = cluster
        self.sg_graph_db = sg_graph_db

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        NagSuppressions.add_stack_suppressions(
            self,
            apply_to_nested_stacks=True,
            suppressions=[
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-N5",
                        "reason": "Cluster is in private subnets, no DB IAM auth enabled",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-EC23",
                        "reason": "Cluster is in private subnets, open to all available IP within VPC",
                    }
                ),
            ],
        )
