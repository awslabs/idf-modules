# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List, Optional, Union, cast

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_fsx as fsx
from aws_cdk import Aspects, CfnTag, Stack, Tags
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class FsxFileSystem(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        deployment_name: str,
        module_name: str,
        vpc_id: str,
        fs_deployment_type: str,
        private_subnet_ids: List[str],
        stack_description: str,
        storage_throughput: Union[int, float, None],
        storage_capacity: int,
        data_bucket_name: Optional[str],
        export_path: Optional[str],
        import_path: Optional[str],
        dra_import_path: Optional[str],
        dra_export_path: Optional[str],
        file_system_type_version: Optional[str],
        import_policy: Optional[str],
        **kwargs: Any,
    ) -> None:
        # Env vars
        self.project_name = project_name
        self.deployment_name = deployment_name
        self.module_name = module_name

        super().__init__(scope, id, description=stack_description, **kwargs)

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"
        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        import_path = f"s3://{data_bucket_name}{import_path}" if import_path else None
        export_path = f"s3://{data_bucket_name}{export_path}" if export_path else None

        self.vpc_id = vpc_id
        self.vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=vpc_id,
        )

        self.private_subnets = []
        self.private_subnet_ids = []
        # subnet id needs to be list
        for idx, subnet_id in enumerate(private_subnet_ids):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(scope=self, id=f"subnet{idx}", subnet_id=subnet_id))
            self.private_subnet_ids.append(str(subnet_id))

        self.fsx_security_group = ec2.SecurityGroup(
            self,
            "FsxSg",
            vpc=self.vpc,
            allow_all_outbound=True,
            security_group_name=f"{self.project_name}-{self.deployment_name}-{self.module_name}-fsx-lustre",
        )

        self.fsx_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(988),
            description="FSx Lustre",
        )

        auto_import_policy = None
        if not (dra_import_path and dra_export_path) and fs_deployment_type not in ["PERSISTENT_1", "PERSISTENT_2"]:
            auto_import_policy = import_policy

        self.fsx_filesystem = fsx.CfnFileSystem(
            self,
            "Fsx",
            file_system_type="LUSTRE",
            storage_capacity=storage_capacity,
            subnet_ids=[self.private_subnet_ids[0]],
            security_group_ids=[self.fsx_security_group.security_group_id],
            tags=[CfnTag(key="Name", value=full_dep_mod)],
            file_system_type_version=file_system_type_version if file_system_type_version else None,
            # Lustre configuration is not supported if you need a data repository association
            lustre_configuration=fsx.CfnFileSystem.LustreConfigurationProperty(
                deployment_type=fs_deployment_type,
                import_path=import_path if fs_deployment_type not in ["PERSISTENT_1", "PERSISTENT_2"] else None,
                export_path=export_path if fs_deployment_type not in ["PERSISTENT_1", "PERSISTENT_2"] else None,
                per_unit_storage_throughput=storage_throughput,
                data_compression_type="LZ4",
                auto_import_policy=auto_import_policy,
            ),
        )
        # Fsx Linking a Persistent 2 file system to an S3 bucket using the LustreConfiguration is not supported

        if dra_import_path and dra_export_path:
            dra_s3_import_path = f"s3://{data_bucket_name}{dra_import_path}" if dra_import_path else None
            dra_s3_export_path = f"s3://{data_bucket_name}{dra_export_path}" if dra_export_path else None

            _dra_import = fsx.CfnDataRepositoryAssociation(
                self,
                "ImportPathDRA",
                data_repository_path=dra_s3_import_path,
                file_system_id=self.fsx_filesystem.ref,
                file_system_path=dra_import_path,
                batch_import_meta_data_on_create=True,
                # imported_file_chunk_size=1024,
                s3=fsx.CfnDataRepositoryAssociation.S3Property(
                    auto_export_policy=fsx.CfnDataRepositoryAssociation.AutoExportPolicyProperty(
                        events=["NEW", "CHANGED", "DELETED"]
                    ),
                    auto_import_policy=fsx.CfnDataRepositoryAssociation.AutoImportPolicyProperty(
                        events=["NEW", "CHANGED", "DELETED"]
                    ),
                ),
            )
            _dra_export = fsx.CfnDataRepositoryAssociation(
                self,
                "ExportPathDRA",
                data_repository_path=dra_s3_export_path,
                file_system_id=self.fsx_filesystem.ref,
                file_system_path=dra_export_path,
                batch_import_meta_data_on_create=True,
                # imported_file_chunk_size=1024,
                s3=fsx.CfnDataRepositoryAssociation.S3Property(
                    auto_export_policy=fsx.CfnDataRepositoryAssociation.AutoExportPolicyProperty(
                        events=["NEW", "CHANGED", "DELETED"]
                    ),
                    auto_import_policy=fsx.CfnDataRepositoryAssociation.AutoImportPolicyProperty(
                        events=["NEW", "CHANGED", "DELETED"]
                    ),
                ),
            )
        Aspects.of(self).add(AwsSolutionsChecks())

        NagSuppressions.add_stack_suppressions(
            self,
            apply_to_nested_stacks=True,
            suppressions=[
                {  # type: ignore
                    "id": "AwsSolutions-IAM4",
                    "reason": "Managed Policies are for service account roles only",
                },
                {  # type: ignore
                    "id": "AwsSolutions-IAM5",
                    "reason": "Resource access restriced to resources",
                },
            ],
        )
