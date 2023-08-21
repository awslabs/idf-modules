# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

import os

import aws_cdk
from aws_cdk import App, CfnOutput

from stack import BucketsStack

project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")
hash = os.getenv("SEEDFARMER_HASH", "")


buckets_encryption_type = os.getenv("SEEDFARMER_PARAMETER_ENCRYPTION_TYPE", "SSE")
buckets_retention = os.getenv("SEEDFARMER_PARAMETER_RETENTION_TYPE", "RETAIN")


app = App()

if len(f"{project_name}-{deployment_name}") > 36:
    raise Exception("This module cannot support a project+deployment name character length greater than 35")

if buckets_retention not in ["DESTROY", "RETAIN"]:
    raise Exception("The only RETENTION_TYPE values accepted are 'DESTROY' and 'RETAIN' ")


if buckets_encryption_type not in ["SSE", "KMS"]:
    raise Exception("The only ENCRYPTION_TYPE values accepted are 'SSE' and 'KMS' ")

stack = BucketsStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,
    module_name=module_name,
    buckets_encryption_type=buckets_encryption_type,
    buckets_retention=buckets_retention,
    hash=hash,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

CfnOutput(
    scope=stack,
    id="metadata",
    value=stack.to_json_string(
        {
            "ArtifactsBucketName": stack.artifacts_bucket.bucket_name,
            "LogsBucketName": stack.logs_bucket.bucket_name,
            "ReadOnlyPolicyArn": stack.readonly_policy.managed_policy_arn,
            "FullAccessPolicyArn": stack.fullaccess_policy.managed_policy_arn,
        }
    ),
)


app.synth(force=True)
