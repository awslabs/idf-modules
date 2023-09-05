# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import pytest


@pytest.fixture(scope="function")
def stack_defaults():
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
    os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
    os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_ID"] = "sid"
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_NAME"] = "sname"
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_VERSION"] = "sversion"

    # Unload the app import so that subsequent tests don't reuse
    if "app" in sys.modules:
        del sys.modules["app"]


def test_app(stack_defaults):
    import app  # noqa: F401


def test_project_deployment_name_length(stack_defaults):
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project-incredibly"

    with pytest.raises(Exception) as e:
        import app  # noqa: F401
    assert "module cannot support a project+deployment name character length greater than" in str(e)


def test_solution_id(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_SOLUTION_ID"]

    with pytest.raises(Exception):
        import app  # noqa: F401

        assert os.environ["SEEDFARMER_PARAMETER_SOLUTION_ID"] == "sid"


def test_solution_name(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_SOLUTION_NAME"]

    with pytest.raises(Exception):
        import app  # noqa: F401

        assert os.environ["SEEDFARMER_PARAMETER_SOLUTION_NAME"] == "sname"


def test_solution_version(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_SOLUTION_VERSION"]

    with pytest.raises(Exception):
        import app  # noqa: F401

        assert os.environ["SEEDFARMER_PARAMETER_SOLUTION_VERSION"] == "sversion"
