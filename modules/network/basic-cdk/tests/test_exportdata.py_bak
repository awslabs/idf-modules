#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def stack_defaults(request):
    os.environ["SEEDFARMER_PROJECT_NAME"] = "test-project"
    os.environ["SEEDFARMER_DEPLOYMENT_NAME"] = "test-deployment"
    os.environ["SEEDFARMER_MODULE_NAME"] = "test-module"

    rootdir = request.config.rootdir
    outpath = Path(rootdir, "cdk-exports.json")
    print(outpath)
    project_name = os.environ["SEEDFARMER_PROJECT_NAME"]
    dep_name = os.environ["SEEDFARMER_DEPLOYMENT_NAME"]
    mod_name = os.environ["SEEDFARMER_MODULE_NAME"]
    cdk_out = f"{project_name}-{dep_name}-{mod_name}"
    payload = {cdk_out: {"metadata": '{"SomeExportedMetadata":"TheValueExportedHere"}'}}
    # Write a sample output Metadata that we can parse
    with open(outpath, "w") as outfile:
        outfile.write(json.dumps(payload))


def test_metadata(stack_defaults, request):
    import export_metadata  # noqa: F401

    with open(Path(request.config.rootdir, "SEEDFARMER_MODULE_METADATA"), "r") as infile:
        meta = infile.read()
    doc = json.loads(meta)
    assert doc.get("SomeExportedMetadata")
