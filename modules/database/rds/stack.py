# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
from typing import Any, cast

import aws_cdk as cdk
import cdk_nag
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as sm
from constructs import Construct, IConstruct


def _get_hosted_rotation_for_engine(engine: str) -> sm.HostedRotation:
    if engine == "mysql":
        return sm.HostedRotation.mysql_single_user()
    elif engine == "postgresql":
        return sm.HostedRotation.postgre_sql_single_user()
    else:
        raise ValueError(f"Unsupported engine: {engine}")


def _get_db_instance_engine(engine: str) -> rds.IInstanceEngine:
    if "mysql" == engine:
        return rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_35)
    elif "postgresql" == engine:
        return rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16_1)
    else:
        raise ValueError(f"Unsupported engine: {engine}")


class RDSDatabaseStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        vpc_id: str,
        subnet_ids: list[str],
        engine: str,
        username: str,
        instance_type: str,
        removal_policy: cdk.RemovalPolicy,
        port: int | None = None,
        stack_description: str | None = None,
        **kwargs: Any,
    ) -> None:

        super().__init__(scope, id, description=stack_description, **kwargs)

        self.project_name = project_name
        self.deployment_name = deployment_name
        self.module_name = module_name

        dep_mod = f"{self.project_name}-{self.deployment_name}-{self.module_name}"
        dep_mod = dep_mod[:64]
        cdk.Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=dep_mod)

        # Create secret and generate password
        self.db_credentials_secret = sm.Secret(
            self,
            "Database Secret",
            secret_name=f"{project_name}-{deployment_name}-{module_name}/db-credentials",
            description=f"Database Secret for {project_name}-{deployment_name}-{module_name}",
            generate_secret_string=sm.SecretStringGenerator(
                secret_string_template=json.dumps({"username": username}),
                generate_string_key="password",
                password_length=20,
                exclude_punctuation=True,
            ),
            removal_policy=removal_policy,
        )

        # Add rotation schedule
        self.db_credentials_secret.add_rotation_schedule(
            "RotationSchedule",
            automatically_after=cdk.Duration.days(90),
            hosted_rotation=_get_hosted_rotation_for_engine(engine),
        )

        # Find VPC and subnets
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)
        private_subnets = [
            ec2.Subnet.from_subnet_id(self, f"Subnet {subnet_id}", subnet_id) for subnet_id in subnet_ids
        ]

        # Create security group for database
        self.sg_rds = ec2.SecurityGroup(
            self,
            "Security Group",
            vpc=vpc,
            security_group_name=f"{project_name}-{deployment_name}-{module_name}-rds-sg",
        )

        # Create database instance
        self.database = rds.DatabaseInstance(
            scope=self,
            id="RDS Database",
            port=port,
            credentials=rds.Credentials.from_secret(self.db_credentials_secret),
            engine=_get_db_instance_engine(engine),
            instance_type=ec2.InstanceType(instance_type),
            vpc=vpc,
            security_groups=[self.sg_rds],
            vpc_subnets=ec2.SubnetSelection(subnets=private_subnets),
            multi_az=True,
            storage_encrypted=True,
            removal_policy=removal_policy,
        )

        # Adds an ingress rule which allows resources in the VPC's CIDR to access the database.
        self.database.connections.allow_default_port_from(
            other=ec2.Peer.ipv4("10.0.0.0/24"),
            description="Allows resources in the VPC CIDR to access the database",
        )

        # Set up CDK nag
        cdk.Aspects.of(self).add(cdk_nag.AwsSolutionsChecks(log_ignores=True))

        nag_supressions: list[cdk_nag.NagPackSuppression] = []
        if port is None:
            nag_supressions.append(
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-RDS11",
                    reason="Default port will be returned as a module output",
                ),
            )
        if removal_policy == cdk.RemovalPolicy.DESTROY:
            nag_supressions.append(
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-RDS10",
                    reason="Retention policy was explicitely set to DESTROY",
                ),
            )
        cdk_nag.NagSuppressions.add_stack_suppressions(self, suppressions=nag_supressions)
