import datetime
import logging
import sys
from typing import Dict, List

import aws_cdk as cdk
import aws_cdk.cloud_assembly_schema as cas
import aws_cdk.integ_tests_alpha as integration
import boto3

sys.path.append("../")

import stack  # noqa: E402

app = cdk.App()
timestamp = datetime.datetime.now()
logger = logging.getLogger(__name__)


def get_module_dependencies(resource_keys: List[str]) -> Dict[str, str]:
    ssm = boto3.client("ssm", region_name="us-east-1")
    dependencies = {}
    try:
        for key in resource_keys:
            dependencies[key] = ssm.get_parameter(Name=f"/module-integration-tests/{key}")["Parameter"]["Value"]
    except Exception as e:
        print(f"issue getting dependencies: {e}")
    return dependencies


dependencies = get_module_dependencies(
    # Add any required resource identifiers here
    resource_keys=[]
)

integration.IntegTest(
    app,
    "Integration Tests EFS Module",
    test_cases=[
        stack.AppRegistry(
            app,
            "app-registry",
            project_name="integ",
            deployment_name="testing",
            module_name="efs",
            solution_id="0123",
            solution_name="app-registry-integ",
            solution_version="x.y.z",
        )
    ],
    regions=["us-east-1"],
    enable_lookups=True,
    diff_assets=True,
    stack_update_workflow=True,
    cdk_command_options=cas.CdkCommands(
        deploy=cas.DeployCommand(args=cas.DeployOptions(require_approval=cas.RequireApproval.NEVER, json=True)),
        destroy=cas.DestroyCommand(args=cas.DestroyOptions(force=True)),
    ),
)
app.synth()
