# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# type: ignore

import os

import aws_cdk
from aws_cdk import App, CfnOutput

from emr_eks import EmrEksStack
from rbac_stack import EmrEksRbacStack

# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


eks_cluster_name = os.getenv(_param("EKS_CLUSTER_NAME"), "")  # required
eks_admin_role_arn = os.getenv(_param("EKS_CLUSTER_ADMIN_ROLE_ARN"), "")  # required
eks_oidc_arn = os.getenv(_param("EKS_OIDC_ARN"), "")  # required
eks_openid_issuer = os.getenv(_param("EKS_OPENID_ISSUER"), "")  # required
emr_eks_namespace = os.getenv(_param("EMR_EKS_NAMESPACE"))  # required
logs_bucket_name = os.getenv(_param("LOGS_BUCKET_NAME"), "")  # required
artifacts_bucket_name = os.getenv(_param("ARTIFACTS_BUCKET_NAME"), "")  # required
eks_handler_rolearn = os.getenv(_param("EKS_HANDLER_ROLEARN"), "")  # required

app = App()

eks_rbac_stack = EmrEksRbacStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}-rbac",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    eks_cluster_name=eks_cluster_name,
    eks_admin_role_arn=eks_admin_role_arn,
    eks_oidc_arn=eks_oidc_arn,
    eks_openid_issuer=eks_openid_issuer,
    eks_handler_rolearn=eks_handler_rolearn,
    emr_eks_namespace=emr_eks_namespace,
    logs_bucket_name=logs_bucket_name,
    artifacts_bucket_name=artifacts_bucket_name,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

emr_eks_airflow = EmrEksStack(
    app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    eks_cluster_name=eks_cluster_name,
    emr_eks_namespace=emr_eks_namespace,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

CfnOutput(
    scope=eks_rbac_stack,
    id="metadata",
    value=eks_rbac_stack.to_json_string(
        {
            "EmrJobExecutionRoleArn": eks_rbac_stack.job_role.role_arn,
        }
    ),
)

CfnOutput(
    scope=emr_eks_airflow,
    id="metadata",
    value=emr_eks_airflow.to_json_string(
        {
            "VirtualClusterId": emr_eks_airflow.emr_vc.attr_id,
        }
    ),
)


app.synth(force=True)
