import datetime
import sys

import aws_cdk as cdk
import aws_cdk.cloud_assembly_schema as cas
import aws_cdk.integ_tests_alpha as integration

sys.path.append("../")

import stack  # noqa: E402

app = cdk.App()
timestamp = datetime.datetime.now()

integration.IntegTest(
    app,
    "Integration Tests Buckets Module",
    test_cases=[
        stack.NetworkingStack(
            app,
            "network-public",
            project_name="integ",
            deployment_name="testing",
            module_name="basic-cdk",
            internet_accessible=True,
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
            internet_accessible=False,
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
