# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from unittest import mock

import pytest


@pytest.fixture(scope="function", autouse=True)
def stack_defaults():
    with mock.patch.dict(os.environ, {}, clear=True):
        os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
        os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
        os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"

        os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
        os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

        os.environ["SEEDFARMER_PARAMETER_RETENTION_TYPE"] = "DESTROY"
        os.environ["SEEDFARMER_PARAMETER_VPC_ID"] = "vpc-12345"

        # Unload the app import so that subsequent tests don't reuse
        if "app" in sys.modules:
            del sys.modules["app"]

        yield


def test_app():
    import app  # noqa: F401


def test_retention_default():
    del os.environ["SEEDFARMER_PARAMETER_RETENTION_TYPE"]

    with pytest.raises(Exception):
        import app  # noqa: F401

        assert os.environ["SEEDFARMER_PARAMETER_RETENTION_TYPE"] == "DESTROY"


def test_project_deployment_name_length():
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project-incredibly-long-name"

    with pytest.raises(Exception) as e:
        import app  # noqa: F401
    assert "module cannot support a project+deployment name character length greater than" in str(e)


def test_invalid_retention_type():
    os.environ["SEEDFARMER_PARAMETER_RETENTION_TYPE"] = "SOMETHINGCRAZY"

    with pytest.raises(Exception) as e:
        import app  # noqa: F401
    assert "The only RETENTION_TYPE values accepted are 'DESTROY' and 'RETAIN'" in str(e)


def test_vpc_id():
    del os.environ["SEEDFARMER_PARAMETER_VPC_ID"]

    with pytest.raises(Exception):
        import app  # noqa: F401

        assert os.environ["SEEDFARMER_PARAMETER_VPC_ID"] == "vpc-12345"
