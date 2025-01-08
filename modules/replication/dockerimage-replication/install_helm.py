import os
import tarfile
import requests
import shutil
from replication_utils.utils import get_credentials
from replication_utils.logging import logger

distro_url = os.getenv("SEEDFARMER_PARAMETER_HELM_DISTRO_URL","https://get.helm.sh/helm-v3.11.3-linux-amd64.tar.gz" )
distro_secret = os.getenv("SEEDFARMER_PARAMETER_HELM_DISTRO_SECRET_NAME", None)
distro_key = os.getenv("SEEDFARMER_PARAMETER_HELM_DISTRO_SECRET_KEY", None)
tar_filename= "helm.tar.gz"
extracted_dir = "linux-amd64"
dest_path = "/usr/local/bin/helm"

def get_distro():
    if distro_secret is None:
        logger.info(f"Using with URL: {distro_url}  without authentication")
        response = requests.get(distro_url, stream=True)
        return response
    else:
        user,pwd = get_credentials(distro_secret,distro_key)
        if user is None or pwd is None:
            logger.info(f"Using with URL: {distro_url}  without authentication as no user/pwd were found with {distro_secret}")
            response = requests.get(distro_url, stream=True)
            return response
        else:
            logger.info(f"Using with URL: {distro_url} with authentication from {distro_secret}")
            response=requests.get(distro_url, stream=True, auth=(user, pwd))
            return response

# Download the tar.gz file
response = get_distro()
if response.status_code == 200:
    with open(tar_filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
else:
    raise Exception(f"Failed to download file: {response.status_code}")

# Extract the tar.gz file
with tarfile.open(tar_filename, "r:gz") as tar:
    tar.extractall()

# Move the helm binary to /usr/local/bin
shutil.move(os.path.join(extracted_dir, "helm"), dest_path)

# Clean up the downloaded tar.gz file and extracted directory
shutil.rmtree(extracted_dir)
os.remove(tar_filename)

logger.info(f"Helm installed successfully at {dest_path}")