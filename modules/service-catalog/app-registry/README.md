# AWS Service Catalog - App Regitsry resources

## Description

You can consider deploying this module, if you are working on creating an AWS Solution. One of the requirements for creating an AWS solution is being able to track the CloudFormation stacks using AWS Service catalog - AppRegistry resource.

This module:

- Creates an AppRegistry application resource
- It also joins the CloudFormation stacks created externally into the AppRegistry application using boto3

## Inputs/Outputs

### Input Parameters

#### Required

- `solution-id`: The solution ID for the AWS Solution
- `solution-name`: The solution Name for the AWS Solution
- `solution-version`: The solution Version for the AWS Solution

### Sample declaration of AWS Batch Compute Configuration

```yaml
parameters:
  - name: solution-id
    value: id
  - name: solution-name
    value: name
  - name: solution-version
    value: version
```

#### Optional

### Module Metadata Outputs

- `AppRegistryName`: Service Catalog - AppRegistry name
- `AttributeGroupName`: Service Catalog - Attribute group name

#### Output Example

```json
{"AppRegistryName":"addf-aws-solutions-wip-catalog-app-reg-AppRegistryApp","AttributeGroupName":"addf-aws-solutions-wip-catalog-app-reg-AppAttributeGroup"}
```
