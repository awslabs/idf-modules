# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os

from aws_cdk import App, CfnOutput, Environment

from stack import FsxFileSystem

LOGGING_FORMAT = "[%(asctime)s][%(filename)-13s:%(lineno)3d] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
_logger: logging.Logger = logging.getLogger(__name__)

project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


vpc_id = os.getenv(_param("VPC_ID"))  # required
private_subnet_ids = json.loads(os.getenv(_param("PRIVATE_SUBNET_IDS")))  # type: ignore # required
fs_deployment_type = os.getenv(_param("FS_DEPLOYMENT_TYPE"), "PERSISTENT_2")  # required
import_path = os.getenv(_param("IMPORT_PATH"), None)
export_path = os.getenv(_param("EXPORT_PATH"), None)
data_bucket_name = os.getenv(_param("DATA_BUCKET_NAME"), None)
storage_throughput = os.getenv(_param("STORAGE_THROUGHPUT"), None)
storage_throughput = int(storage_throughput) if storage_throughput else None  # type: ignore
fsx_version = os.getenv(_param("FSX_VERSION"), "2.12")
import_policy = os.getenv(_param("IMPORT_POLICY"), "NONE")
storage_capacity = int(os.getenv(_param("STORAGE_CAPACITY"), 1200))

if not vpc_id:
    raise ValueError("missing input parameter vpc-id")

if fsx_version == "2.10":
    if fs_deployment_type == "PERSISTENT_2" and data_bucket_name is not None and import_path is not None:
        raise ValueError("File system deployment type `PERSISTENT_2` does not support an S3 import path")

    if fs_deployment_type == "PERSISTENT_2" and data_bucket_name is not None and export_path is not None:
        raise ValueError("File system deployment type `PERSISTENT_2` does not support an S3 export path")

if fs_deployment_type not in ["SCRATCH_1", "SCRATCH_2", "PERSISTENT_2", "PERSISTENT_1"]:
    raise ValueError("We only suppprt deployment types of SCRATCH_1, SCRATCH_2, PERSISTENT_2, PERSISTENT_1")

if "SCRATCH" in fs_deployment_type and storage_throughput is not None:
    _logger.warning(
        f"The storage throughput can not be specified for fs_deployment_type={fs_deployment_type}. Setting to None"
    )
    storage_throughput = None

if "PERSISTENT" in fs_deployment_type and storage_throughput is None:
    raise ValueError(f"The storage throughput must be specified for Lustre fs_deployment_type={fs_deployment_type}")


if fs_deployment_type in ["SCRATCH_2", "PERSISTENT_2", "PERSISTENT_1"]:
    if storage_capacity not in [1200, 2400] and (storage_capacity % 2400) != 0:
        raise ValueError(
            f"{fs_deployment_type} storage_capacity must be 1200, 2400 or an increment of 2400 - see README"
        )
else:
    if storage_capacity not in [1200, 2400] and (storage_capacity % 3600) != 0:
        raise ValueError(
            f"{fs_deployment_type} storage_capacity must be 1200, 2400 or an increment of 3600 - see README"
        )

if import_policy.upper() not in ["NONE", "NEW", "NEW_CHANGED", "NEW_CHANGED_DELETED"]:
    raise ValueError("import_policy must be one of NEW, NEW_CHANGED, NEW_CHANGED_DELETED")

if import_policy.upper() not in ["NONE"] and "SCRATCH_1" in fs_deployment_type:
    raise ValueError("SCRATCH_1 does not support Import Policy")


def fix_paths(p: str) -> str:
    if p:
        return f"/{p}" if not p.startswith("/") else p
    else:
        return p


def generate_description() -> str:
    soln_id = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_ID", None)
    soln_name = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_NAME", None)
    soln_version = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_VERSION", None)

    desc = "IDF - Fsx-Lustre"
    if soln_id and soln_name and soln_version:
        desc = f"({soln_id}) {soln_name}. Version {soln_version}"
    elif soln_id and soln_name:
        desc = f"({soln_id}) {soln_name}"
    return desc


app = App()

stack = FsxFileSystem(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    data_bucket_name=data_bucket_name,
    fs_deployment_type=fs_deployment_type,
    module_name=module_name,
    private_subnet_ids=private_subnet_ids,
    vpc_id=vpc_id,
    import_path=fix_paths(import_path),  # type: ignore
    export_path=fix_paths(export_path),  # type: ignore
    storage_throughput=storage_throughput,  # type: ignore
    storage_capacity=storage_capacity,
    file_system_type_version=fsx_version,
    stack_description=generate_description(),
    import_policy=import_policy,
    env=Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]),
)

fsx_lustre_fs_deployment_type = stack.fsx_filesystem.lustre_configuration.deployment_type  # type: ignore

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "FSxLustreAttrDnsName": stack.fsx_filesystem.attr_dns_name,
            "FSxLustreFileSystemId": stack.fsx_filesystem.ref,
            "FSxLustreSecurityGroup": stack.fsx_security_group.security_group_id,
            "FSxLustreMountName": stack.fsx_filesystem.attr_lustre_mount_name,
            "FSxLustreFileSystemDeploymentType": fsx_lustre_fs_deployment_type,
            "FSxLustreVersion": stack.fsx_filesystem.file_system_type_version,
            "FSxLustreStorageCapacity": stack.fsx_filesystem.storage_capacity,
        }
    ),
)

app.synth(force=True)
