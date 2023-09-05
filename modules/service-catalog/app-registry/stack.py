# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, cast

import cdk_nag
from aws_cdk import Aspects, Aws, Stack, Tags
from aws_cdk import aws_servicecatalogappregistry as appregistry
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class AppRegistry(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        deployment_name: str,
        module_name: str,
        solution_id: str,
        solution_name: str,
        solution_version: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            scope,
            id,
            description="Deploy AWS AppRegistry to visualize resources related to an AWS Solution",
            **kwargs,
        )

        dep_mod = f"{project_name}-{deployment_name}-{module_name}"

        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        """
        dep_mod is used to name OpenSearch domain and the max length cant exceed 28 characters
        https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html
        """

        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        self.solution_name = solution_name
        self.solution_id = solution_id
        self.solution_version = solution_version

        # App registry
        self.app_registry = appregistry.CfnApplication(
            self,
            f"{full_dep_mod}-AppRegistryApp",
            name=f"{full_dep_mod}-AppRegistryApp",
            description=f"Service Catalog app to visualize resources for the solution {self.solution_name}",
            tags={
                "Solutions:SolutionID": self.solution_id,
                "Solutions:SolutionName": self.solution_name,
                "Solutions:SolutionVersion": self.solution_version,
            },
        )

        # Attributes group
        self.attribute_group = appregistry.CfnAttributeGroup(
            self,
            f"{full_dep_mod}-AppAttributeGroup",
            name=f"{full_dep_mod}-AppAttributeGroup",
            description="Attributes for Solutions Metadata",
            attributes={
                "version": self.solution_version,
                "solutionID": self.solution_id,
                "solutionName": self.solution_name,
            },
        )

        # Attribute association
        attribute_group_association = appregistry.CfnAttributeGroupAssociation(
            self,
            f"{full_dep_mod}-AttributeGroupAssociation",
            application=self.app_registry.name,
            attribute_group=self.attribute_group.name,
        )
        attribute_group_association.node.add_dependency(self.app_registry)
        attribute_group_association.node.add_dependency(self.attribute_group)

        # Stack association
        cfn_resource_association = appregistry.CfnResourceAssociation(
            self,
            f"{full_dep_mod}-AppResourceAssociation",
            application=self.app_registry.name,
            resource=Aws.STACK_NAME,
            resource_type="CFN_STACK",
        )
        cfn_resource_association.node.add_dependency(self.app_registry)

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        NagSuppressions.add_stack_suppressions(
            self,
            apply_to_nested_stacks=True,
            suppressions=[
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM4",
                        "reason": "Managed Policies are for service account roles only",
                    }
                ),
                NagPackSuppression(
                    **{
                        "id": "AwsSolutions-IAM5",
                        "reason": "Resource access restriced to IDF resources",
                    }
                ),
            ],
        )
