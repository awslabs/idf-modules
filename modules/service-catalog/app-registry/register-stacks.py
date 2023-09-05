#!/usr/env/bin python

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Registers CloudFormation stacks into AppRegistry"""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError

APPREG_CLIENT = boto3.client("servicecatalog-appregistry")
CFN_CLIENT = boto3.client("cloudformation")
PROJECT_NAME = os.getenv("SEEDFARMER_PROJECT_NAME", "addf")
DEP_NAME = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "aws-solutions-wip")
APP_REG_NAME = json.loads(os.getenv("SEEDFARMER_MODULE_METADATA"))["AppRegistryName"]
ACTION = sys.argv[1]


def main():

    stacks_tobe_registsred = _list_stacks(prefix=f"{PROJECT_NAME}-{DEP_NAME}")

    if ACTION == "associate":
        _asaociate_stacks(stacks=stacks_tobe_registsred)
    else:
        _dissaociate_stacks(stacks=stacks_tobe_registsred)


def _asaociate_stacks(stacks):
    for stack in stacks:
        try:
            APPREG_CLIENT.associate_resource(application=APP_REG_NAME, resourceType="CFN_STACK", resource=stack)
            print(f"Associated the stack: {stack} successfully")
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"Could not find the stack: {stack} associated")
                continue
            else:
                raise ex


def _dissaociate_stacks(stacks):
    for stack in stacks:
        try:
            APPREG_CLIENT.disassociate_resource(application=APP_REG_NAME, resourceType="CFN_STACK", resource=stack)
            print(f"Disassociated the stack: {stack} successfully")
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"Could not find the stack: {stack} associated")
                continue
            else:
                raise ex


def _list_stacks(prefix):
    """List CFN Stacks by the desired prefix"""

    stacks_tobe_registsred = []

    response = CFN_CLIENT.list_stacks(StackStatusFilter=["CREATE_COMPLETE"])

    for stack in response["StackSummaries"]:
        if stack["StackName"].startswith(prefix):
            stacks_tobe_registsred.append(stack["StackName"])

    print("The list of stacks: {}".format(stacks_tobe_registsred))
    return stacks_tobe_registsred


if __name__ == "__main__":
    main()
