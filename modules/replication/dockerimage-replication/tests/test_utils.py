# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

import unittest

from helmparser.logging import boto3_logger, logger
from helmparser.utils.utils import deep_merge


class TestMain(unittest.TestCase):
    def test_deep_merge(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 3, "c": 4}
        d3 = {"c": 5, "d": 6}

        result = deep_merge(d1, d2, d3)
        self.assertEqual(result, {"a": 1, "b": 3, "c": 5, "d": 6})

    def test_logger_main(self):
        with self.assertLogs("main", level="INFO") as cm:
            logger.info("first message")
            self.assertEqual(cm.output, ["INFO:main:first message"])

    def test_logger_boto3(self):
        with self.assertLogs("boto3", level="INFO") as cm:
            boto3_logger.info("first message")
            self.assertEqual(cm.output, ["INFO:boto3:first message"])
