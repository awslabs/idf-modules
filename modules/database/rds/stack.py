# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
from typing import Any, Literal, cast

import aws_cdk as cdk
import cdk_nag
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as sm
from constructs import Construct, IConstruct


def _get_hosted_rotation_for_engine(engine: str, vpc: ec2.IVpc, vpc_subnets: ec2.SubnetSelection) -> sm.HostedRotation:
    if engine == "mysql":
        return sm.HostedRotation.mysql_single_user(vpc=vpc, vpc_subnets=vpc_subnets)
    elif engine == "postgresql":
        return sm.HostedRotation.postgre_sql_single_user(vpc=vpc, vpc_subnets=vpc_subnets)
    else:
        raise ValueError(f"Unsupported engine: {engine}")


def _get_db_instance_engine(engine: str, version: str) -> rds.IInstanceEngine:
    if "mysql" == engine:
        return rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.of(version, version))
    elif "postgresql" == engine:
        return rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.of(version, version))
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
        engine: Literal["mysql", "postgresql"],
        engine_version: str,
        database_name: str,
        username: str,
        credential_rotation_days: int,
        instance_type: str,
        removal_policy: cdk.RemovalPolicy,
        is_accessible_from_vpc: bool = False,
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

        # Find VPC and subnets
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)
        vpc_subnets = ec2.SubnetSelection(
            subnets=[ec2.Subnet.from_subnet_id(self, f"Subnet {subnet_id}", subnet_id) for subnet_id in subnet_ids]
        )

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
        if credential_rotation_days > 0:
            self.db_credentials_secret.add_rotation_schedule(
                "Rotation",
                automatically_after=cdk.Duration.days(credential_rotation_days),
                hosted_rotation=_get_hosted_rotation_for_engine(engine, vpc, vpc_subnets),
            )

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
            database_name=database_name,
            credentials=rds.Credentials.from_secret(self.db_credentials_secret),
            engine=_get_db_instance_engine(engine, engine_version),
            instance_type=ec2.InstanceType(instance_type),
            vpc=vpc,
            security_groups=[self.sg_rds],
            vpc_subnets=vpc_subnets,
            multi_az=True,
            storage_encrypted=True,
            removal_policy=removal_policy,
        )

        if is_accessible_from_vpc:
            # Adds an ingress rule which allows resources in the VPC's CIDR to access the database.
            self.database.connections.allow_default_port_from(
                other=ec2.Peer.ipv4(vpc.vpc_cidr_block),
                description="Allows resources in the VPC CIDR to access the database",
            )

        # Set up CDK nag suppressions
        if port is None:
            cdk_nag.NagSuppressions.add_resource_suppressions(
                self.database,
                suppressions=[
                    cdk_nag.NagPackSuppression(
                        id="AwsSolutions-RDS11",
                        reason="Default port will be returned as a module output",
                    ),
                ],
            )
        if removal_policy == cdk.RemovalPolicy.DESTROY:
            cdk_nag.NagSuppressions.add_resource_suppressions(
                self.database,
                suppressions=[
                    cdk_nag.NagPackSuppression(
                        id="AwsSolutions-RDS10",
                        reason="Retention policy was explicitely set to DESTROY",
                    ),
                    cdk_nag.NagPackSuppression(
                        id="AwsSolutions-RDS15",
                        reason="Retention policy was explicitely set to DESTROY",
                    ),
                ],
            )
        if credential_rotation_days == 0:
            cdk_nag.NagSuppressions.add_resource_suppressions(
                self.db_credentials_secret,
                suppressions=[
                    cdk_nag.NagPackSuppression(
                        id="AwsSolutions-SMG4",
                        reason="Rotation was not enabled",
                    ),
                ],
            )
