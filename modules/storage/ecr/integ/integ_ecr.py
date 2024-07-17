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
    "Integration Tests ECR Module",
    test_cases=[
        stack.EcrStack(
            scope=app,
            construct_id="ecr",
            repository_name="integ",
            image_tag_mutability="MUTABLE",
            lifecycle_max_image_count=None,
            lifecycle_max_days=None,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            image_scan_on_push=True,
            encryption="KMS_MANAGED",
            kms_key_arn=None,
            description=f"Integration Test: {timestamp.month}-{timestamp.day} {timestamp.hour}:{timestamp.minute}",
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
