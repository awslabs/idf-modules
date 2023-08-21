"""Argument parsing module"""

# ######################################################################################################################
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                  #
#                                                                                                                      #
#  Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance      #
#  with the License. You may obtain a copy of the License at                                                           #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed    #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for   #
#  the specific language governing permissions and limitations under the License.                                      #
# ######################################################################################################################


import argparse


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Generates list of images to sync",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbosity",
        help="increase verbosity",
    )

    parser.add_argument(
        "-u",
        "--update-helm-repos",
        action="store_true",
        dest="update_helm",
        help="update helm repositories",
    )

    parser.add_argument(
        "-e",
        "--eks-version",
        action="store",
        default="1.25",
        dest="eks_version",
        help="specify eks version",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-d",
        "--versions-directory",
        action="store",
        dest="versions_dir",
        help="provide path to the versions directory",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-p",
        "--registry-prefix",
        action="store",
        dest="registry_prefix",
        help="provide registry prefix",
        type=str,
        required=True,
    )

    return parser.parse_args(args)
