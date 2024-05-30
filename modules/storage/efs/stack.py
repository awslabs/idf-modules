# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, cast

import cdk_nag
from aws_cdk import Aspects, RemovalPolicy, Stack, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_efs as efs
from aws_cdk import aws_iam as iam
from constructs import Construct, IConstruct

project_dir = os.path.dirname(os.path.abspath(__file__))


class EFSFileStorage(Stack):  # type: ignore
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        vpc_id: str,
        efs_removal_policy: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            scope,
            id,
            description="This stack creates an Amazon EFS filesystem",
            **kwargs,
        )

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"
        dep_mod = dep_mod[0:19]
        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        self.vpc_id = vpc_id
        self.vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=self.vpc_id,
        )

        self.efs_security_group = ec2.SecurityGroup(self, "EFSSecurityGroup", vpc=self.vpc, allow_all_outbound=True)
        self.efs_filesystem = efs.FileSystem(
            self,
            "Filesystem",
            vpc=self.vpc,
            security_group=self.efs_security_group,
            removal_policy=RemovalPolicy.DESTROY if efs_removal_policy in ["DESTROY"] else RemovalPolicy.RETAIN,
        )

        cfn_efs_filesystem = cast(efs.CfnFileSystem, self.efs_filesystem.node.default_child)
        cfn_efs_filesystem.file_system_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    principals=[iam.AnyPrincipal()],
                    actions=[
                        "elasticfilesystem:ClientMount",
                        "elasticfilesystem:ClientWrite",
                        "elasticfilesystem:ClientRootAccess",
                    ],
                    resources=["*"],
                    conditions={"Bool": {"elasticfilesystem:AccessedViaMountTarget": "true"}},
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    principals=[iam.AnyPrincipal()],
                    actions=["*"],
                    resources=["*"],
                    conditions={"Bool": {"aws:SecureTransport": "false"}},
                ),
            ]
        )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())
