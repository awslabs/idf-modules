import pytest
from unittest.mock import patch
import json

from get_list_eks_images import (
    update_helm,
    fetch_chart_info,
    apply_image_mapping,
    apply_chart_info,
)


@pytest.fixture
def mock_workloads_data():
    workload_path = "tests/test_payloads/test_workload_policy_reporter.json"
    with open(workload_path, encoding="utf-8") as workload_file:
        return json.load(workload_file)


def mock_helm_show(command, chart_name, version):
    show_path = "tests/test_payloads/test_charts.json"
    with open(show_path, encoding="utf-8") as chart_show_file:
        show_data = json.load(chart_show_file)
    if command == "chart":
        return show_data["kyverno_policy_reporter"]["chart"]
    elif command == "values":
        return show_data["kyverno_policy_reporter"]["values"]
    return {}


def mock_show_subchart(project_path, workload, name, subchart, version):
    show_subchart_path = "tests/test_subchart_policy_reporter.json"
    with open(show_subchart_path, encoding="utf-8") as subchart_file:
        return json.load(subchart_file)


@patch("get_list_eks_images.helm.show", side_effect=mock_helm_show)
@patch("get_list_eks_images.helm.show_subchart", side_effect=mock_show_subchart)
def test_fetch_chart_info(mock_show_subchart, mock_helm_show, mock_workloads_data):
    # Call the function being tested
    result = fetch_chart_info(mock_workloads_data)

    # Load expected result
    with open("tests/test_payloads/test_charts_policy_reporter.json", encoding="utf-8") as workload_file:
        test_case_result = json.load(workload_file)

    # Assert the result matches the expected output
    assert result == test_case_result

