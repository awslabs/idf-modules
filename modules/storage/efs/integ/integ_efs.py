import datetime
import sys

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.cloud_assembly_schema as cas
import aws_cdk.integ_tests_alpha as integration

sys.path.append("../")

import stack  # noqa: E402

app = cdk.App()
timestamp = datetime.datetime.now()

class EFSFileStorageWithDependencies(stack.EFSFileStorage):
    def __init__(self, scope):
        vpc = ec2.Vpc(scope, "EFS Integ VPC")

        super().__init__(
            scope,
            "efs",
            project_name="integ",
            deployment_name="testing",
            module_name="efs",
            vpc_id=vpc.vpc_id,
            efs_removal_policy="DESTROY",
            stack_descrption=f"Integration Test: {timestamp.month}-{timestamp.day} {timestamp.hour}:{timestamp.minute}",
        )

integration.IntegTest(
    app,
    "Integration Tests EFS Module",
    test_cases=[
        EFSFileStorageWithDependencies(app)
    ],
    diff_assets=True,
    stack_update_workflow=True,
    cdk_command_options=cas.CdkCommands(
        deploy=cas.DeployCommand(args=cas.DeployOptions(require_approval=cas.RequireApproval.NEVER, json=True)),
        destroy=cas.DestroyCommand(args=cas.DestroyOptions(force=True)),
    ),
)
app.synth()
