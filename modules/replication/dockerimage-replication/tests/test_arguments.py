# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

import unittest

from helmparser.arguments import parse_args


class TestArguments(unittest.TestCase):
    def test_arguments(self):
        parser = parse_args(["-e", "1.25", "-d", "tests_versions", "-p", "000000"])
        self.assertEqual(parser.eks_version, "1.25")
        self.assertEqual(parser.versions_dir, "tests_versions")
        self.assertEqual(parser.registry_prefix, "000000")
        self.assertFalse(parser.update_helm)

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-h"])

        self.assertEqual(cm.exception.code, 0)

    def test_empty_args(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args([])

        self.assertEqual(cm.exception.code, 2)
