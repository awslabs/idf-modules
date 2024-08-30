import argparse
import boto3
import glob
import json
import os
from pprint import pprint
from typing import Dict, List

CWD = os.getcwd()
s3 = boto3.resource("s3")

parser = argparse.ArgumentParser(description="Generate module metadata")
parser.add_argument("-v", "--version", help="Version", required=True)
parser.add_argument("-b", "--bucket-name", help="S3 Bucket Name", required=True)
parser.add_argument("-n", "--repo-name", help="Repo Name", required=True)
parser.add_argument(
    "--org-name", help="Github Organization Name", default="awslabs", required=False
)
parser.add_argument(
    "-i",
    "--ignore-regex",
    help="Regex pattern to ignore from collection",
    required=False,
)

args = parser.parse_args()


def get_all_module_paths(dir: str, level: int) -> List[str]:
    pattern = dir + level * "/*"
    return [d[len(CWD) :] for d in glob.glob(pattern) if os.path.isdir(d)]


def generate_module_metadata(module_path: str) -> Dict[str, str]:
    data = {}
    data["name"] = f"{module_path.split('/')[2]}-{module_path.split('/')[3]}"
    data["version"] = args.version
    # Add error handling and case-insensitive filtering
    data["readme"] = open(f"{CWD}{module_path}/README.md", "r").read()
    data["source_url"] = (
        f"https://github.com/{args.org_name}/{args.repo_name}/tree/release/{args.version}{module_path}"
    )
    data["git_path"] = (
        f"git::https://github.com/{args.org_name}/{args.repo_name}.git/{module_path}/?ref=release/{args.version}"
    )
    return data


def print_metadata(metadata: Dict[str, str]) -> None:
    result = {}
    for k, v in metadata.items():
        if k == "readme":
            v = "..."
        result[k] = v
    pprint(result)


def write_metadata_to_s3(key: str, metadata: Dict[str, str]) -> None:
    path = f"module-metadata/{key}/versions/{args.version}/metadata.json"
    print(f"[*] writing metadata to path: {path}")
    object = s3.Object(args.bucket_name, path)
    object.put(Body=bytes(json.dumps(metadata).encode("UTF-8")))


module_paths = get_all_module_paths(f"{CWD}/modules", 2)

print(f"*** Module Metadata for version {args.version} ***")
for path in module_paths:
    metadata = generate_module_metadata(path)
    write_metadata_to_s3(metadata["name"], metadata)  # To Implement
    print_metadata(metadata)
