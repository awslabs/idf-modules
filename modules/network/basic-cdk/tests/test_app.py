# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys

import pytest


@pytest.fixture(scope="function")
def stack_defaults():
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
    os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
    os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"
    os.environ["SEEDFARMER_HASH"] = "xxxxxxxx"
    os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"] = "true"
    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

    # Unload the app import so that subsequent tests don't reuse
    if "app" in sys.modules:
        del sys.modules["app"]


def test_app(stack_defaults):
    import app  # noqa: F401


def test_internet_default(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"]
    os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"] = "true"
    import app  # noqa: F401

    assert app.internet_accessible is True


def test_internet_bad_value(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"]
    os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"] = "fsfadsfasdfsa"
    with pytest.raises(json.decoder.JSONDecodeError) as e:
        import app  # noqa: F401
    assert "JSONDecodeError" in str(e)


def test_internet_false(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"]
    os.environ["SEEDFARMER_PARAMETER_INTERNET_ACCESSIBLE"] = "false"
    import app  # noqa: F401

    assert app.internet_accessible is False


def test_solution_description(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_ID"] = "SO123456"
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_NAME"] = "MY GREAT TEST"
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_VERSION"] = "v1.0.0"

    import app

    ver = app.generate_description()
    assert ver == "(SO123456) MY GREAT TEST. Version v1.0.0"


def test_solution_description_no_version(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_ID"] = "SO123456"
    os.environ["SEEDFARMER_PARAMETER_SOLUTION_NAME"] = "MY GREAT TEST"
    del os.environ["SEEDFARMER_PARAMETER_SOLUTION_VERSION"]

    import app

    ver = app.generate_description()
    assert ver == "(SO123456) MY GREAT TEST"
