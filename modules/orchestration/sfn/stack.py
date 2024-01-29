# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from os import path
from os.path import abspath, dirname
from typing import Any, Dict, List, Optional, Union, cast

import aws_cdk
import aws_cdk.aws_cloudwatch as cw
import aws_cdk.aws_iam as iam
import aws_cdk.aws_stepfunctions as sfn
import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


def get_definition_body(
    definition: Optional[Union[sfn.IChainable, str]],
    definition_file: Optional[str]
    ) -> sfn.DefinitionBody:
  
    if definition and definition_file: 
        raise("Only one of 'definition' or 'definitionFile' should be provided.");
    if (not definition and not definition_file):
        raise("One of 'definition' or 'definitionFile' must be provided.");
    if definition_file:
        return sfn.DefinitionBody.from_file(definition_file)
    else:
        if type(definition) == "str":
            return sfn.DefinitionBody.from_string(definition)
        else:
            return sfn.DefinitionBody.from_chainable(definition)

class SFNStack(Stack):  # type: ignore
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        stack_description: str,
        definition: Optional[sfn.IChainable],
        definition_file: Optional[str],
        state_machine_name: Optional[str] = None,
        additional_role_policy_statements: Optional[List[iam.PolicyStatement]] = None,
        state_machine_failed_executions_alarm_threshold: Optional[int] = 1,
        state_machine_failed_executions_alarm_evaluation_periods: Optional[int] = 1,
        alarms_enabled: Optional[bool] = True,
        **kwargs: Any,
    ) -> None:
        """
        Build state machine.

        Parameters
        ----------
        id : str
            Identifier of the state machine
        environment_id : str
            Identifier of the environment
        definition : Optional[IChainable]
            State machine definition
        definition_file: Optional[str]
            File or json definition of StateMachine.
        state_machine_input : Optional[Dict[str, Any]]
            Input of the state machine
        state_machine_name : Optional[str]
            Name of state machine
        additional_role_policy_statements : Optional[List[PolicyStatement]]
            Additional IAM policy statements to add to the state machine role
        state_machine_failed_executions_alarm_threshold: Optional[int]
            The number of failed state machine executions before triggering CW alarm. Defaults to `1`
        state_machine_failed_executions_alarm_evaluation_periods: Optional[int]
            The number of periods over which data is compared to the specified threshold. Defaults to `1`
        alarms_enabled: Optional[bool]
            CloudWatch Alarm enabled. Defaults to `true`
        kwargs: Any
            Additional paramaters to pass to State Machine creation.
        """
        super().__init__(scope, id, description=stack_description, **kwargs)

        # CDK Env Vars
        account: str = aws_cdk.Aws.ACCOUNT_ID
        region: str = aws_cdk.Aws.REGION

        # IDF Env vars
        dep_mod = f"{project_name}-{deployment_name}-{module_name}"

        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod

        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        self.state_machine = sfn.StateMachine(
            self, 
            "State Machine",
            definition_body=get_definition_body(definition, definition_file),
            state_machine_name=state_machine_name,
        )

        if additional_role_policy_statements:
            for statement in additional_role_policy_statements:
                self.state_machine.add_to_role_policy(statement)

        if alarms_enabled:
            cw.Alarm(
                self, 
                "State Machine Failure Alarm",
                metric=self.state_machine.metric_failed(),
                comparisonOperator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
                threshold=state_machine_failed_executions_alarm_threshold,
                evaluationPeriods=state_machine_failed_executions_alarm_evaluation_periods,
            )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks(verbose=True))

        bucket_suppression = [
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-S1",
                    "reason": "Logs are disabled for demo purposes",
                }
            ),
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-S5",
                    "reason": "No OAI needed - no one is accessing this data without explicit permissions",
                }
            ),
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-IAM5",
                    "reason": "Resource access restriced to IDF resources",
                }
            ),
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-IAM4",
                    "reason": "Managed Policies are for service account roles only",
                }
            ),
        ]

        NagSuppressions.add_stack_suppressions(self, bucket_suppression)
