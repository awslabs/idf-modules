

## Running Integ Runnner
---

#### Prerequisites
- npm
- python & pip

#### Example Script 
```shell
# Install Dependencies
pip install -r requirements.txt

# Get Version
CDK_VERSION=$(python -c "from importlib.metadata import version; print(version('aws_cdk_lib'))")

# Install integ-tests package
pip install aws-cdk.integ-tests-alpha==${CDK_VERSION}a0

# Install integ-runner Cli 
npm i -g aws-cdk@${CDK_VERSION}
npm i -g @aws-cdk/integ-runner@${CDK_VERSION}-alpha.0
npm i --save-dev esbuild@0

# Run Integration Tests
integ-runner --language python --update-on-failed --directory integ/
```