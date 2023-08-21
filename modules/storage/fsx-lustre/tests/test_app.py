# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

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

    os.environ["SEEDFARMER_PARAMETER_VPC_ID"] = "vpc-12345"
    os.environ["SEEDFARMER_PARAMETER_PRIVATE_SUBNET_IDS"] = '["subnet-1234","subnet-5678"]'
    os.environ["SEEDFARMER_PARAMETER_FS_DEPLOYMENT_TYPE"] = "PERSISTENT_1"
    os.environ["SEEDFARMER_PARAMETER_IMPORT_PATH"] = "somepathin/"
    os.environ["SEEDFARMER_PARAMETER_EXPORT_PATH"] = "somepatout/"
    os.environ["SEEDFARMER_PARAMETER_DATA_BUCKET_NAME"] = "thbucketname"
    os.environ["SEEDFARMER_PARAMETER_STORAGE_THROUGHPUT"] = "50"

    # Unload the app import so that subsequent tests don't reuse
    if "app" in sys.modules:
        del sys.modules["app"]


def test_app(stack_defaults):
    import app  # noqa: F811 F401


def test_vpcid_missing(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_VPC_ID"]

    with pytest.raises(Exception):
        import app  # noqa: F811 F401


def test_subnets_missing(stack_defaults):
    del os.environ["SEEDFARMER_PARAMETER_PRIVATE_SUBNET_IDS"]

    with pytest.raises(TypeError):
        import app  # noqa: F811 F401


def test_subnets_invalid(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_PRIVATE_SUBNET_IDS"] = "messedupjson"

    with pytest.raises(Exception):
        import app  # noqa: F811 F401


def test_fs_storage_types_invalid(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_FS_DEPLOYMENT_TYPE"] = "PERSISTENT_2"
    with pytest.raises(Exception):
        import app  # noqa: F811 F401

    del os.environ["SEEDFARMER_PARAMETER_IMPORT_PATH"]
    with pytest.raises(Exception):
        import app  # noqa: F811 F401

    os.environ["SEEDFARMER_PARAMETER_IMPORT_PATH"] = "/somepath"
    del os.environ["SEEDFARMER_PARAMETER_EXPORT_PATH"]
    with pytest.raises(Exception):
        import app  # noqa: F811 F401

    os.environ["SEEDFARMER_PARAMETER_IMPORT_PATH"] = "/somepath"
    os.environ["SEEDFARMER_PARAMETER_EXPORT_PATH"] = "/sompath"
    del os.environ["SEEDFARMER_PARAMETER_DATA_BUCKET_NAME"]
    import app  # noqa: F811 F401

    os.environ["SEEDFARMER_PARAMETER_IMPORT_PATH"] = "/somepath"
    del os.environ["SEEDFARMER_PARAMETER_EXPORT_PATH"]
    import app  # noqa: F811 F401


def test_fs_storage_types(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_FS_DEPLOYMENT_TYPE"] = "PERSISTENT_1"
    import app  # noqa: F811 F401


def test_throughput_persistent_validation(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_FS_DEPLOYMENT_TYPE"] = "PERSISTENT_1"
    del os.environ["SEEDFARMER_PARAMETER_STORAGE_THROUGHPUT"]
    with pytest.raises(Exception):
        import app  # noqa: F811 F401


def test_throughput_scratch_validation(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_FS_DEPLOYMENT_TYPE"] = "SCRATCH_1"
    import app  # noqa: F811 F401


def test_throughput_invalid(stack_defaults):
    os.environ["SEEDFARMER_PARAMETER_STORAGE_THROUGHPUT"] = "text"
    with pytest.raises(Exception):
        import app  # noqa: F811 F401
