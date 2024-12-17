# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List, Optional, cast

import aws_cdk.aws_ec2 as ec2
import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from cdk_nag import NagPackSuppression, NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)

VPC_CIDR = "10.0.0.0/16"
SUBNET_SIZE = 24


class NetworkingStack(Stack):  # type: ignore
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_name: str,
        deployment_name: str,
        module_name: str,
        vpc_cidr: Optional[str],
        cidr_mask: Optional[int],
        internet_accessible: bool,
        local_zones: Optional[List[str]],
        stack_description: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, description=stack_description, **kwargs)
        dep_mod = f"{project_name}-{deployment_name}-{module_name}"
        # Stitch the below with `hash` to make it unique
        dep_mod = dep_mod[:19]
        # used to tag AWS resources. Tag Value length cant exceed 256 characters
        full_dep_mod = dep_mod[:256] if len(dep_mod) > 256 else dep_mod
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=full_dep_mod)

        self.vpc: ec2.Vpc = self._create_vpc(
            internet_accessible=internet_accessible, local_zones=local_zones, vpc_cidr=vpc_cidr, cidr_mask=cidr_mask
        )

        self.internet_accessible = internet_accessible
        self.public_subnets = (
            self.vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC)
            if self.vpc.public_subnets
            else self.vpc.select_subnets(subnet_group_name="")
        )
        self.private_subnets = (
            self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)  # type: ignore
            if self.vpc.private_subnets
            else self.vpc.select_subnets(subnet_group_name="")
        )
        if not internet_accessible:
            self.isolated_subnets = (
                self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)  # type: ignore
                if self.vpc.isolated_subnets
                else self.vpc.select_subnets(subnet_group_name="")
            )
            self.nodes_subnets = self.isolated_subnets
        else:
            self.nodes_subnets = self.private_subnets

        # Create the VPC security group
        self._vpc_security_group = self._create_vpc_security_group()

        if not internet_accessible:
            self._create_vpc_endpoints()

        # Add Aspects
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        # Add suppressions
        self._add_suppressions()

    def _create_vpc(
        self,
        internet_accessible: bool,
        local_zones: Optional[List[str]],
        vpc_cidr: Optional[str],
        cidr_mask: Optional[int],
    ) -> ec2.Vpc:
        subnet_configuration = self._get_subnet_configuration(internet_accessible)
        nat = ec2.NatProvider.gateway()
        vpc = ec2.Vpc(
            scope=self,
            id="vpc",
            default_instance_tenancy=ec2.DefaultInstanceTenancy.DEFAULT,
            cidr=vpc_cidr,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=3,
            nat_gateways=1,
            nat_gateway_provider=nat,
            subnet_configuration=subnet_configuration,
        )

        if local_zones != []:
            self.local_zone_private_subnets = self._create_local_zone_private_subnets(vpc, nat, local_zones)
            self.local_zone_public_subnets = self._create_local_zone_public_subnets(vpc, local_zones)

        # Enable VPC Flow Logs
        self._enable_vpc_flow_logs(vpc)

        # Tag subnets for EKS
        self._tag_subnets_for_eks(vpc)

        return vpc

    def _enable_vpc_flow_logs(self, vpc: ec2.Vpc) -> None:
        vpc.add_flow_log(
            "FlowLogCloudWatch",
            traffic_type=ec2.FlowLogTrafficType.ALL,
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(),
        )

    def _get_subnet_configuration(self, internet_accessible: bool) -> List[ec2.SubnetConfiguration]:
        if internet_accessible:
            return [
                ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=SUBNET_SIZE),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=SUBNET_SIZE,
                ),
            ]
        else:
            return [
                ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=SUBNET_SIZE),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=SUBNET_SIZE,
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=SUBNET_SIZE,
                ),
            ]

    def _create_local_zone_private_subnets(
        self, vpc: ec2.Vpc, nat: ec2.NatProvider, local_zones: Optional[List[str]]
    ) -> List[ec2.PrivateSubnet]:
        subnets = []
        for i, zone in enumerate(local_zones):  # type: ignore
            i = 12 + i
            subnets.append(
                ec2.PrivateSubnet(
                    self,
                    id=f"LocalZonePrivate-{zone}",
                    availability_zone=zone,
                    vpc_id=vpc.vpc_id,
                    cidr_block=f"10.0.{i}.0/{SUBNET_SIZE}",
                )
            )

        for subnet in range(len(local_zones)):  # type: ignore
            subnets[subnet].add_default_nat_route(nat.configured_gateways[0].gateway_id)

        return subnets

    def _create_local_zone_public_subnets(
        self, vpc: ec2.Vpc, local_zones: Optional[List[str]]
    ) -> List[ec2.PublicSubnet]:
        subnets = []
        for i, zone in enumerate(local_zones):  # type: ignore
            i = 16 + i
            public_subnet = ec2.PublicSubnet(
                self,
                id=f"LocalZonePublic-{zone}",
                availability_zone=zone,
                vpc_id=vpc.vpc_id,
                cidr_block=f"10.0.{i}.0/{SUBNET_SIZE}",
                map_public_ip_on_launch=True,
            )
            public_subnet.add_default_internet_route(vpc.internet_gateway_id, vpc.internet_connectivity_established)  # type: ignore
            subnets.append(public_subnet)
        return subnets

    def _tag_subnets_for_eks(self, vpc: ec2.Vpc) -> None:
        self._tag_subnets(vpc.private_subnets, "kubernetes.io/role/internal-elb")
        self._tag_subnets(vpc.public_subnets, "kubernetes.io/role/elb")

    @staticmethod
    def _tag_subnets(subnets: List[ec2.ISubnet], tag: str) -> None:
        for subnet in subnets:
            Tags.of(subnet).add(tag, "1")

    def _create_vpc_endpoints(self) -> None:
        # Creating Gateway Endpoints
        self._create_gateway_vpc_endpoints()
        # Creating Interface Endpoints
        self._create_interface_vpc_endpoints()

    def _create_gateway_vpc_endpoints(self) -> None:
        vpc_gateway_endpoints = {
            "s3": ec2.GatewayVpcEndpointAwsService.S3,
            "dynamodb": ec2.GatewayVpcEndpointAwsService.DYNAMODB,
        }
        for name, gateway_vpc_endpoint_service in vpc_gateway_endpoints.items():
            self.vpc.add_gateway_endpoint(
                id=name,
                service=gateway_vpc_endpoint_service,
                subnets=[
                    ec2.SubnetSelection(subnets=self.nodes_subnets.subnets),
                ],
            )

    def _create_interface_vpc_endpoints(self) -> None:
        vpc_interface_endpoints = {
            "cloudwatch_endpoint": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            "cloudwatch_logs_endpoint": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            "cloudwatch_events": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS,
            "ecr_docker_endpoint": ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            "ecr_endpoint": ec2.InterfaceVpcEndpointAwsService.ECR,
            "ec2_endpoint": ec2.InterfaceVpcEndpointAwsService.EC2,
            "ecs": ec2.InterfaceVpcEndpointAwsService.ECS,
            "ecs_agent": ec2.InterfaceVpcEndpointAwsService.ECS_AGENT,
            "ecs_telemetry": ec2.InterfaceVpcEndpointAwsService.ECS_TELEMETRY,
            "git_endpoint": ec2.InterfaceVpcEndpointAwsService.CODECOMMIT_GIT,
            "ssm_endpoint": ec2.InterfaceVpcEndpointAwsService.SSM,
            "ssm_messages_endpoint": ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
            "secrets_endpoint": ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            "kms_endpoint": ec2.InterfaceVpcEndpointAwsService.KMS,
            "sagemaker_endpoint": ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_API,
            "sagemaker_runtime": ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_RUNTIME,
            "notebook_endpoint": ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_NOTEBOOK,
            "athena_endpoint": ec2.InterfaceVpcEndpointAwsService("athena"),
            "glue_endpoint": ec2.InterfaceVpcEndpointAwsService("glue"),
            "sqs": ec2.InterfaceVpcEndpointAwsService.SQS,
            "step_function_endpoint": ec2.InterfaceVpcEndpointAwsService("states"),
            "sns_endpoint": ec2.InterfaceVpcEndpointAwsService.SNS,
            "kinesis_firehose_endpoint": ec2.InterfaceVpcEndpointAwsService("kinesis-firehose"),
            "api_gateway": ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
            "sts_endpoint": ec2.InterfaceVpcEndpointAwsService.STS,
            "efs": ec2.InterfaceVpcEndpointAwsService.ELASTIC_FILESYSTEM,
            "elb": ec2.InterfaceVpcEndpointAwsService.ELASTIC_LOAD_BALANCING,
            "lambda": ec2.InterfaceVpcEndpointAwsService.LAMBDA_,
            "code_artifact_repo_endpoint": ec2.InterfaceVpcEndpointAwsService("codeartifact.repositories"),
            "code_artifact_api_endpoint": ec2.InterfaceVpcEndpointAwsService("codeartifact.api"),
            "autoscaling": ec2.InterfaceVpcEndpointAwsService("autoscaling"),
            "cloudformation_endpoint": ec2.InterfaceVpcEndpointAwsService("cloudformation"),
            "codebuild_endpoint": ec2.InterfaceVpcEndpointAwsService("codebuild"),
            "emr-containers": ec2.InterfaceVpcEndpointAwsService("emr-containers"),
            "databrew": ec2.InterfaceVpcEndpointAwsService("databrew"),
            "bedrock": ec2.InterfaceVpcEndpointAwsService("bedrock"),
            # "bedrock_agent": ec2.InterfaceVpcEndpointAwsService("bedrock-agent"),
            # "bedrock_agent_runtime": ec2.InterfaceVpcEndpointAwsService("bedrock-agent-runtime"),
            "bedrock_runtime": ec2.InterfaceVpcEndpointAwsService("bedrock-runtime"),
            "prometheus": ec2.InterfaceVpcEndpointAwsService.PROMETHEUS,
            "prometheus_workspaces": ec2.InterfaceVpcEndpointAwsService.PROMETHEUS_WORKSPACES,
        }

        for name, interface_service in vpc_interface_endpoints.items():
            self.vpc.add_interface_endpoint(
                id=name,
                service=interface_service,
                subnets=ec2.SubnetSelection(subnets=self.nodes_subnets.subnets),
                private_dns_enabled=True,
                security_groups=[cast(ec2.ISecurityGroup, self._vpc_security_group)],
            )

        # Adding Redshift endpoints with CDK low level APIs
        endpoint_url_template = "com.amazonaws.{}.{}"
        ec2.CfnVPCEndpoint(
            self,
            "redshift_endpoint",
            vpc_endpoint_type="Interface",
            service_name=endpoint_url_template.format(self.region, "redshift"),
            vpc_id=self.vpc.vpc_id,
            security_group_ids=[self._vpc_security_group.security_group_id],
            subnet_ids=self.nodes_subnets.subnet_ids,
            private_dns_enabled=True,
        )

    def _create_vpc_security_group(self) -> ec2.SecurityGroup:
        vpc_sg = ec2.SecurityGroup(self, "vpc-sg", vpc=cast(ec2.IVpc, self.vpc), allow_all_outbound=False)
        vpc_sg.add_ingress_rule(peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block), connection=ec2.Port.all_tcp())

        return vpc_sg

    def _add_suppressions(self) -> None:
        suppressions = [
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-VPC7",
                    "reason": "Flowlogs not enabled for this module",
                }
            ),
            NagPackSuppression(
                **{
                    "id": "AwsSolutions-EC23",
                    "reason": "Intrinsic Function Warning",
                }
            ),
        ]
        NagSuppressions.add_stack_suppressions(self, suppressions)
