# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import aws_cdk as cdk
import cdk_nag

from settings import ApplicationSettings
from stack import RDSDatabaseStack

app = cdk.App()
app_settings = ApplicationSettings()

template_stack = RDSDatabaseStack(
    scope=app,
    id=app_settings.seedfarmer_settings.app_prefix,
    project_name=app_settings.seedfarmer_settings.project_name,
    deployment_name=app_settings.seedfarmer_settings.deployment_name,
    module_name=app_settings.seedfarmer_settings.module_name,
    stack_description=app_settings.module_settings.description,
    vpc_id=app_settings.module_settings.vpc_id,
    subnet_ids=app_settings.module_settings.subnet_ids,
    database_name=app_settings.module_settings.database_name,
    engine=app_settings.module_settings.engine,
    engine_version=app_settings.module_settings.engine_version,
    username=app_settings.module_settings.admin_username,
    credential_rotation_days=app_settings.module_settings.credential_rotation_days,
    is_accessible_from_vpc=app_settings.module_settings.is_accessible_from_vpc,
    port=app_settings.module_settings.port,
    removal_policy=app_settings.module_settings.removal_policy,
    instance_type=app_settings.module_settings.instance_type,
    env=cdk.Environment(
        account=app_settings.cdk_settings.account,
        region=app_settings.cdk_settings.region,
    ),
)


cdk.CfnOutput(
    scope=template_stack,
    id="metadata",
    value=template_stack.to_json_string(
        {
            "CredentialsSecretArn": template_stack.db_credentials_secret.secret_arn,
            "DatabaseHostname": template_stack.database.instance_endpoint.hostname,
            "DatabasePort": template_stack.database.instance_endpoint.port,
            "SecurityGroupId": template_stack.sg_rds.security_group_id,
        }
    ),
)

cdk.Aspects.of(template_stack).add(cdk_nag.AwsSolutionsChecks(log_ignores=True))

app.synth()
