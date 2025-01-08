# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from  typing import Optional, Tuple
import boto3
import json
from botocore.exceptions import ClientError

USER="username"
PWD ="password"

def get_credentials(secret_name:str, secret_key:Optional[str]=None)->Tuple[Optional[str],Optional[str]]:
    if not secret_name:
        return (None, None)
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',region_name="us-east-1")
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Error fetching secret, check the name and make sure you have permissions -- {e}")
        exit(1)
    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    secret = secret[secret_key] if secret_key else secret
    if USER in secret and PWD in secret:
        return (secret[USER], secret[PWD])
    else:
        return (None, None)

