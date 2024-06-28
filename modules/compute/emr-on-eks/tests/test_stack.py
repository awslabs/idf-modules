# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template


@pytest.fixture(scope="function")
def stack_defaults():
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
    os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
    os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

    if "stack" in sys.modules:
        del sys.modules["stack"]


def test_synthesize_rbac_stack(stack_defaults):
    import rbac_stack

    app = cdk.App()
    proj_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    stack = rbac_stack.EmrEksRbacStack(
        scope=app,
        id=f"{proj_name}-{dep_name}-{mod_name}",
        project_name=proj_name,
        deployment_name=dep_name,
        module_name=mod_name,
        eks_cluster_name="cluster",
        eks_admin_role_arn="arn:aws:iam::123456789012:role/eks-admin-role",
        eks_oidc_arn="arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/XXXXXX",
        eks_openid_issuer="oidc.eks.us-east-1.amazonaws.com/id/XXXXXX",
        eks_handler_rolearn="arn:aws:iam::123456789012:role/HandlerRole",
        logs_bucket_name="logs-bucket",
        artifacts_bucket_name="artifacts-bucket",
        emr_eks_namespace="emr-eks-ns",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(stack)
    template.resource_count_is("AWS::CloudFormation::Stack", 1)


def test_synthesize_emr_eks_stack(stack_defaults):
    import emr_eks

    app = cdk.App()
    proj_name = "test-project"
    dep_name = "test-deployment"
    mod_name = "test-module"

    stack = emr_eks.EmrEksStack(
        scope=app,
        id=f"{proj_name}-{dep_name}-{mod_name}",
        project_name=proj_name,
        deployment_name=dep_name,
        module_name=mod_name,
        eks_cluster_name="cluster",
        emr_eks_namespace="emr-eks-ns",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
    )

    template = Template.from_stack(stack)
    template.resource_count_is("AWS::EMRContainers::VirtualCluster", 1)
