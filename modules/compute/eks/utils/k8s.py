# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List


def convert_node_labels_to_k8sargs(labels_dict: Dict[str, str]) -> str:
    """
    Converts a dictionary of node labels to a comma separated string in the format used by k8s.
    """
    # e.g i/p. labels_dict = {"usage": "gpu", "nvidia.com/gpu.present": "true"}
    # e.g o/p  usage=gpu,nvidia.com/gpu.present=true
    return ",".join(["=".join(label) for label in labels_dict.items()])


def convert_taints_to_k8sargs(taints_dict: List[Dict[str, str]]) -> str:
    """
    Converts a list of taints to a comma separated string in the format used by k8s.
    """
    # e.g i/p. taints_dict=[{"key": "nvidia.com/gpu", "value": "true", "effect": "NoSchedule"}]
    # e.g o/p  nvidia.com/gpu:NoSchedule
    return ",".join(f"{i['key']}:{i['effect']}" for i in taints_dict)
