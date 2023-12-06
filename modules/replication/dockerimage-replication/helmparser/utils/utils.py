# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from copy import deepcopy
from typing import Any, Dict

from deepmerge import always_merger


def deep_merge(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merges two dictionaries

    Returns:
        dict: Merged dictionary
    """
    merged: Dict[Any, Any] = {}
    for d in dicts:
        tmp = deepcopy(d)
        merged = always_merger.merge(merged, tmp)
    return merged
