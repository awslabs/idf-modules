# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                
                                                                                                                  
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    
# with the License. A copy of the License is located at                                                             
                                                                                                                  
#     http://www.apache.org/licenses/LICENSE-2.0                                                                    
                                                                                                                  
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES 
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    
# and limitations under the License.

import unittest
from unittest import mock
from unittest.mock import mock_open

from helmparser.helm import commands


class TestCommands(unittest.TestCase):
    @mock.patch("subprocess.Popen")
    def test_add_repo(self, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {
            "communicate.return_value": ("output", "error"),
        }
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        commands.add_repo("name", "repo")
        self.assertTrue(mock_subproc_popen.called)

    @mock.patch("subprocess.Popen")
    def test_show(self, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {
            "communicate.return_value": ("output", "error"),
        }
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        commands.show("subcommand", "chart", "version")
        self.assertTrue(mock_subproc_popen.called)

    @mock.patch("shutil.rmtree")
    @mock.patch("builtins.open", mock_open(read_data="data"))
    @mock.patch("os.path.isdir")
    @mock.patch("subprocess.Popen")
    def test_show_subchart(self, mock_subproc_popen, patched_isfile, rm_mock):
        patched_isfile.return_value = True
        rm_mock.return_value = "REMOVED"
        process_mock = mock.Mock()
        attrs = {
            "communicate.return_value": ("output", "error"),
        }
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        commands.show_subchart("project_path", "repo", "subcommand", "chart", "version")
        self.assertTrue(mock_subproc_popen.called)

    @mock.patch("subprocess.Popen")
    def test_update_repos(self, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {
            "communicate.return_value": ("output", "error"),
        }
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        commands.update_repos()
        self.assertTrue(mock_subproc_popen.called)


if __name__ == "__main__":
    unittest.main()

    print("Everything passed")
