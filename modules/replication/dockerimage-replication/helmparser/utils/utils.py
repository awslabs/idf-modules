# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

from copy import deepcopy

from deepmerge import always_merger


def deep_merge(*dicts: dict) -> dict:
    """Merges two dictionaries

    Returns:
        dict: Merged dictionary
    """
    merged = {}
    for d in dicts:
        tmp = deepcopy(d)
        merged = always_merger.merge(merged, tmp)
    return merged
