"""Logging module"""

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

import logging

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
stream_handler.setFormatter(formatter)

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

boto3_logger = logging.getLogger("boto3")
boto3_logger.setLevel(logging.WARN)
boto3_logger.addHandler(stream_handler)
