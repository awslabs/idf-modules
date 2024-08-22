import datetime
import os
import sys

import aws_cdk as cdk
import aws_cdk.cloud_assembly_schema as cas
import aws_cdk.integ_tests_alpha as integration
import boto3

sys.path.append("../")

import stack  # noqa: E402

app = cdk.App()
timestamp = datetime.datetime.now()

ec2_client = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
response = ec2_client.describe_availability_zones()
availability_zones = [az["ZoneName"] for az in response["AvailabilityZones"]][:3]

integration.IntegTest(
    app,
    "Integration Tests Basic Module",
    test_cases=[
        stack.NetworkingStack(
            app,
            "network-public",
            project_name="integ",
            deployment_name="testing",
            module_name="basic-cdk",
            vpc_cidr="10.0.0.0/16",
            cidr_mask=24,
            internet_accessible=True,
            local_zones=availability_zones,
            stack_description=f"""
            Integration Test: {timestamp.month}-{timestamp.day} {timestamp.hour}:{timestamp.minute}
            """,
        ),
        stack.NetworkingStack(
            app,
            "network-private",
            project_name="integ",
            deployment_name="testing",
            module_name="basic-cdk",
            vpc_cidr="10.0.0.0/16",
            cidr_mask=24,
            internet_accessible=False,
            local_zones=availability_zones,
            stack_description=f"""
            Integration Test: {timestamp.month}-{timestamp.day} {timestamp.hour}:{timestamp.minute}
            """,
        ),
    ],
    diff_assets=True,
    stack_update_workflow=True,
    cdk_command_options=cas.CdkCommands(
        deploy=cas.DeployCommand(args=cas.DeployOptions(require_approval=cas.RequireApproval.NEVER, json=True)),
        destroy=cas.DestroyCommand(args=cas.DestroyOptions(force=True)),
    ),
)
app.synth()
