import unittest
from unittest import mock

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
