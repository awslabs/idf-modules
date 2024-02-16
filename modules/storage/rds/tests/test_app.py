# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import pytest


@pytest.fixture(scope="function", autouse=True)
def stack_defaults() -> None:
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
    os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
    os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"
    os.environ["SEEDFARMER_PARAMETER_REMOVAL_POLICY"] = "DESTROY"
    os.environ["SEEDFARMER_PARAMETER_VPC_ID"] = "vpc-12345"
    os.environ["SEEDFARMER_PARAMETER_SUBNET_IDS"] = json.dumps(["subnet-12345", "subnet-67890"])
    os.environ["SEEDFARMER_PARAMETER_ENGINE"] = "mysql"
    os.environ["SEEDFARMER_PARAMETER_ADMIN_USERNAME"] = "admin"

    if "app" in sys.modules:
        del sys.modules["app"]


def test_app() -> None:
    import app  # noqa: F401


def test_project_deployment_name_length() -> None:
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project-incredibly"

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

    assert "module cannot support a project+deployment name character length greater than" in str(e)


@pytest.mark.parametrize("param", [
    "SEEDFARMER_PARAMETER_VPC_ID",
    "SEEDFARMER_PARAMETER_SUBNET_IDS",
    "SEEDFARMER_PARAMETER_ENGINE",
    "SEEDFARMER_PARAMETER_ADMIN_USERNAME"
])
def test_missing_parameter(param: str) -> None:
    del os.environ[param]

    with pytest.raises(Exception):
        import app  # noqa: F401

    assert f"The following environment variable is required: {param}"


def test_retention_default() -> None:
    del os.environ["SEEDFARMER_PARAMETER_REMOVAL_POLICY"]

    import app  # noqa: F401

    assert "SEEDFARMER_PARAMETER_REMOVAL_POLICY" not in os.environ


def test_invalid_retention_type() -> None:
    os.environ["SEEDFARMER_PARAMETER_REMOVAL_POLICY"] = "SOMETHINGCRAZY"

    with pytest.raises(ValueError):
        import app  # noqa: F401

    assert "The only RETENTION_TYPE values accepted are 'DESTROY' and 'RETAIN'"


def test_invalid_engine() -> None:
    os.environ["SEEDFARMER_PARAMETER_ENGINE"] = "MADEUPSQL"

    with pytest.raises(ValueError):
        import app  # noqa: F401

    assert "The only ENGINE values accepted are 'mysql' and 'postgres'"
