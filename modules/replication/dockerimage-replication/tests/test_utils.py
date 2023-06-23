#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import unittest

from helmparser.utils.utils import deep_merge
from helmparser.logging import logger, boto3_logger


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
