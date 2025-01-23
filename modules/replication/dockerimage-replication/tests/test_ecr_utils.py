# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from replication.ecr.ecr_utils import ECRUtils


@pytest.fixture
def mock_boto_client():
    """Fixture to mock boto3 client."""
    with patch("replication.ecr.ecr_utils.boto3.client") as mock_client:
        yield mock_client.return_value


@pytest.fixture
def ecr_utils(mock_boto_client):
    """Fixture to create an instance of ECRUtils with mocked dependencies."""
    return ECRUtils("123456789012", "us-west-2", "amazonaws.com")


@pytest.fixture
def mock_subprocess_popen():
    """Fixture to mock subprocess.Popen."""
    with patch("subprocess.Popen") as mock_popen:
        mock_instance = MagicMock()
        mock_instance.stdout = MagicMock()
        mock_popen.return_value = mock_instance
        yield mock_popen, mock_instance


@pytest.fixture
def mock_subprocess_run():
    """Fixture to mock subprocess.run."""
    with patch("subprocess.run") as mock_run:
        yield mock_run


def test_login_to_ecr_docker_success(mock_subprocess_popen, mock_subprocess_run, ecr_utils):
    """Test successful ECR login for Docker."""
    mock_popen, mock_popen_instance = mock_subprocess_popen
    mock_popen_instance.stdout.read.return_value = "mocked-password"

    mock_run = mock_subprocess_run
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "Login Succeeded"

    result = ecr_utils.login_to_ecr(type="docker")

    assert result is True
    mock_popen.assert_called_once_with(
        ["aws", "ecr", "get-login-password", "--region", "us-west-2"], shell=False, stdout=subprocess.PIPE
    )
    mock_run.assert_called_once_with(
        ["docker", "login", "--username", "AWS", "--password-stdin", "123456789012.dkr.ecr.us-west-2.amazonaws.com"],
        stdin=mock_popen_instance.stdout,
        shell=False,
        capture_output=True,
        text=True,
    )


def test_login_to_ecr_docker_failure(mock_subprocess_popen, mock_subprocess_run, ecr_utils):
    """Test failed ECR login for Docker."""
    mock_popen, mock_popen_instance = mock_subprocess_popen
    mock_popen_instance.stdout.read.return_value = "mocked-password"

    mock_run = mock_subprocess_run
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "Login Failed"

    result = ecr_utils.login_to_ecr(type="docker")

    assert result is False
    mock_popen.assert_called_once_with(
        ["aws", "ecr", "get-login-password", "--region", "us-west-2"], shell=False, stdout=subprocess.PIPE
    )
    mock_run.assert_called_once_with(
        ["docker", "login", "--username", "AWS", "--password-stdin", "123456789012.dkr.ecr.us-west-2.amazonaws.com"],
        stdin=mock_popen_instance.stdout,
        shell=False,
        capture_output=True,
        text=True,
    )


def test_login_to_ecr_helm_success(mock_subprocess_popen, mock_subprocess_run, ecr_utils):
    """Test successful ECR login for Helm."""
    mock_popen, mock_popen_instance = mock_subprocess_popen
    mock_popen_instance.stdout.read.return_value = "mocked-password"

    mock_run = mock_subprocess_run
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "Login Succeeded"

    result = ecr_utils.login_to_ecr(type="helm")

    assert result is True
    mock_popen.assert_called_once_with(
        ["aws", "ecr", "get-login-password", "--region", "us-west-2"], shell=False, stdout=subprocess.PIPE
    )
    mock_run.assert_called_once_with(
        [
            "helm",
            "registry",
            "login",
            "--username",
            "AWS",
            "--password-stdin",
            "123456789012.dkr.ecr.us-west-2.amazonaws.com",
        ],
        stdin=mock_popen_instance.stdout,
        shell=False,
        capture_output=True,
        text=True,
    )


def test_repository_exists(mock_boto_client, ecr_utils):
    # Simulate repository exists
    mock_boto_client.describe_repositories.return_value = {}
    assert ecr_utils.repository_exists("test-repo") is True
    mock_boto_client.describe_repositories.assert_called_once_with(repositoryNames=["test-repo"])


def test_create_repository(mock_boto_client, ecr_utils):
    # Create a mock exception class
    class RepositoryNotFoundException(Exception):
        pass

    mock_boto_client.exceptions.RepositoryNotFoundException = RepositoryNotFoundException
    mock_boto_client.describe_repositories.side_effect = RepositoryNotFoundException
    ecr_utils.create_repository("new-repo-new")
    # Assert create_repository was called
    mock_boto_client.create_repository.assert_called_once_with(
        repositoryName="new-repo-new", imageScanningConfiguration={"scanOnPush": True}
    )

    # Simulate repository exists
    mock_boto_client.describe_repositories.side_effect = None
    mock_boto_client.describe_repositories.return_value = {}
    ecr_utils.create_repository("existing-repo")

    # Assert create_repository was not called again
    mock_boto_client.create_repository.assert_called_once()


def test_image_exists(mock_boto_client, ecr_utils):
    # Simulate image exists
    mock_boto_client.batch_get_image.return_value = {"images": [{"imageId": {"imageTag": "latest"}}]}
    assert ecr_utils.image_exists("repo-name", "latest") is True

    # Simulate image does not exist
    mock_boto_client.batch_get_image.return_value = {"images": []}
    assert ecr_utils.image_exists("repo-name", "non-existent-tag") is False

    # Simulate repository not found
    mock_boto_client.batch_get_image.side_effect = mock_boto_client.exceptions.RepositoryNotFoundException
    assert ecr_utils.image_exists("non-existent-repo", "latest") is False


def test_cleanup_ecr_repos(mock_boto_client, ecr_utils):
    # Simulate paginator response
    mock_boto_client.get_paginator.return_value.paginate.return_value = [
        {"repositories": [{"repositoryName": "test-prefix-repo1"}, {"repositoryName": "test-prefix-repo2"}]}
    ]

    ecr_utils.cleanup_ecr_repos(prefix="test-prefix")

    mock_boto_client.delete_repository.assert_any_call(repositoryName="test-prefix-repo1", force=True)
    mock_boto_client.delete_repository.assert_any_call(repositoryName="test-prefix-repo2", force=True)
    assert mock_boto_client.delete_repository.call_count == 2
