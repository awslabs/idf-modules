# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import aws_cdk
from aws_cdk import App

from stack import SFNStack

# Project specific
project_name = os.getenv("SEEDFARMER_PROJECT_NAME", "")
deployment_name = os.getenv("SEEDFARMER_DEPLOYMENT_NAME", "")
module_name = os.getenv("SEEDFARMER_MODULE_NAME", "")

if len(f"{project_name}-{deployment_name}") > 36:
    raise ValueError("This module cannot support a project+deployment name character length greater than 35")


def _param(name: str) -> str:
    return f"SEEDFARMER_PARAMETER_{name}"


# App specific
definition = os.getenv(_param("STATE_MACHINE_DEFINITION"))
definition_file = os.getenv(_param("PRIVATE_SUBNET_IDS"), "")
state_machine_name = os.getenv(_param("STATE_MACHINE_NAME"))
additional_role_policy_statements = os.getenv(_param("ADDITIONAL_ROLE_POLICY_STATEMENTS"))
state_machine_failed_executions_alarm_threshold = os.getenv(_param("STATE_MACHINE_ALARM_THRESHOLD"))
state_machine_failed_executions_alarm_evaluation_periods = os.getenv(_param("STATE_MACHINE_ALARM_EVALUATION_PERIODS"))
alarms_enabled = os.getenv(_param("ALARMS_ENABLED"))


def generate_description() -> str:
    soln_id = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_ID", None)
    soln_name = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_NAME", None)
    soln_version = os.getenv("SEEDFARMER_PARAMETER_SOLUTION_VERSION", None)

    desc = "IDF - MWAA Module"
    if soln_id and soln_name and soln_version:
        desc = f"({soln_id}) {soln_name}. Version {soln_version}"
    elif soln_id and soln_name:
        desc = f"({soln_id}) {soln_name}"
    return desc


app = App()


stack = SFNStack(
    scope=app,
    id=f"{project_name}-{deployment_name}-{module_name}",
    project_name=project_name,
    deployment_name=deployment_name,  # type: ignore
    module_name=module_name,  # type: ignore
    stack_description=generate_description(),
    definition=definition,
    definition_file=definition_file,
    state_machine_name=state_machine_name,
    additional_role_policy_statements=additional_role_policy_statements,
    state_machine_failed_executions_alarm_evaluation_periods=state_machine_failed_executions_alarm_evaluation_periods,
    state_machine_failed_executions_alarm_threshold=state_machine_failed_executions_alarm_threshold,
    alarms_enabled=alarms_enabled,
    env=aws_cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

app.synth(force=True)
