import sys

sys.path.append("../")
import datetime
import uuid

import aws_cdk as cdk
import aws_cdk.cloud_assembly_schema as cas
import aws_cdk.integ_tests_alpha as integration

import stack

app = cdk.App()
timestamp = datetime.datetime.now()

integration.IntegTest(
    app,
    "Integration Tests Buckets Module",
    test_cases=[
        stack.BucketsStack(
            app,
            "buckets",
            "integ",
            "testing",
            "buckets",
            str(uuid.uuid4())[:8],
            "S3",
            "DESTROY",
            f"Integration Test: {timestamp.month}-{timestamp.day} {timestamp.hour}:{timestamp.minute}",
        )
    ],
    diff_assets=True,
    stack_update_workflow=True,
    cdk_command_options=cas.CdkCommands(
        deploy=cas.DeployCommand(args=cas.DeployOptions(require_approval=cas.RequireApproval.NEVER, json=True)),
        destroy=cas.DestroyCommand(args=cas.DestroyOptions(force=True)),
    ),
)
app.synth()
