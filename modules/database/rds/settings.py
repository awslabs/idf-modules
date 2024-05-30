"""Defines the stack settings."""

from __future__ import annotations

from abc import ABC
from typing import List, Optional

import aws_cdk as cdk
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Literal


class EnvBaseSettings(BaseSettings, ABC):
    """Defines common configuration for settings."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        protected_namespaces=(),
        extra="ignore",
        populate_by_name=True,
    )


class ModuleSettings(EnvBaseSettings):
    """Seedfarmer Parameters.

    These parameters are required for the module stack.
    """

    model_config = SettingsConfigDict(env_prefix="SEEDFARMER_PARAMETER_")

    vpc_id: str
    subnet_ids: List[str]

    engine: Literal["mysql", "postgresql"]
    engine_version: str
    admin_username: str
    database_name: str

    port: Optional[int] = Field(default=None, ge=1, le=65535)
    instance_type: str = Field(default="ml.m5.large")
    credential_rotation_days: int = Field(default=0, ge=0)
    is_accessible_from_vpc: bool = Field(default=False)
    removal_policy: cdk.RemovalPolicy = Field(default=cdk.RemovalPolicy.RETAIN)

    solution_id: Optional[str] = Field(default=None)
    solution_name: Optional[str] = Field(default=None)
    solution_version: Optional[str] = Field(default=None)

    @computed_field  # type: ignore
    @property
    def description(self) -> str:
        if self.solution_id and self.solution_name and self.solution_version:
            return f"({self.solution_id}) {self.solution_name}. Version {self.solution_version}"

        if self.solution_id and self.solution_name:
            return f"({self.solution_id}) {self.solution_name}"

        return "My Module Default Description"


class SeedFarmerSettings(EnvBaseSettings):
    """Seedfarmer Settings.

    These parameters comes from seedfarmer by default.
    """

    model_config = SettingsConfigDict(env_prefix="SEEDFARMER_")

    project_name: str
    deployment_name: str
    module_name: str

    @computed_field  # type: ignore
    @property
    def app_prefix(self) -> str:
        """Application prefix."""
        prefix = "-".join([self.project_name, self.deployment_name, self.module_name])
        return prefix

    @model_validator(mode="after")
    def check_character_length(self) -> "SeedFarmerSettings":
        if len(f"{self.project_name}-{self.deployment_name}") > 35:
            raise ValueError("This module cannot support a project+deployment name character length greater than 35")

        return self


class CDKSettings(EnvBaseSettings):
    """CDK Default Settings.

    These parameters comes from AWS CDK by default.
    """

    model_config = SettingsConfigDict(env_prefix="CDK_DEFAULT_")

    account: str
    region: str


class ApplicationSettings(EnvBaseSettings):
    """Application settings."""

    seedfarmer_settings: SeedFarmerSettings = Field(default_factory=SeedFarmerSettings)
    module_settings: ModuleSettings = Field(default_factory=ModuleSettings)
    cdk_settings: CDKSettings = Field(default_factory=CDKSettings)
