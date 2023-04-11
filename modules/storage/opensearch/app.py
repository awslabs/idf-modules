import json
import os

import aws_cdk
from aws_cdk import App, CfnOutput

from stack import OpenSearchStack


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")
hash = os.getenv("SEEDFARMER_HASH", "")

if len(f"{project_name}-{deployment_name}") > 36:
    raise Exception("This module cannot support a project+deployment name character length greater than 35")

# App specific

vpc_id = os.getenv(_param("VPC_ID"))
private_subnet_ids = json.loads(os.getenv(_param("PRIVATE_SUBNET_IDS")))  # type: ignore
os_domain_retention = os.getenv(_param("RETENTION_TYPE"), "RETAIN")


if not vpc_id:
    raise Exception("missing input parameter vpc-id")

if not private_subnet_ids:
    raise Exception("missing input parameter private-subnet-ids")

if os_domain_retention not in ["DESTROY", "RETAIN"]:
    raise Exception("The only RETENTION_TYPE values accepted are 'DESTROY' and 'RETAIN' ")

os_data_nodes = int(os.getenv(_param("OPENSEARCH_DATA_NODES"), 1))
os_data_node_instance_type = os.getenv(_param("OPENSEARCH_DATA_NODES_INSTANCE_TYPE"), "r6g.large.search")
os_master_nodes = int(os.getenv(_param("OPENSEARCH_MASTER_NODES"), 0))
os_master_node_instance_type = os.getenv(_param("OPENSEARCH_MASTER_NODES_INSTANCE_TYPE"), "r6g.large.search")
os_ebs_volume_size = int(os.getenv(_param("OPENSEARCH_EBS_VOLUME_SIZE"), 10))

# REF: developerguide/supported-instance-types.html


app = App()

stack = OpenSearchStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    hash=hash,
    vpc_id=vpc_id,
    private_subnet_ids=private_subnet_ids,
    os_domain_retention=os_domain_retention,
    os_data_nodes=os_data_nodes,
    os_data_node_instance_type=os_data_node_instance_type,
    os_master_nodes=os_master_nodes,
    os_master_node_instance_type=os_master_node_instance_type,
    os_ebs_volume_size=os_ebs_volume_size,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "OpenSearchDomainEndpoint": stack.domain_endpoint,
            "OpenSearchDashboardUrl": stack.dashboard_url,
            "OpenSearchSecurityGroupId": stack.os_sg_id,
            "OpenSearchDomainName": stack.domain_name,
        }
    ),
)


app.synth(force=True)
