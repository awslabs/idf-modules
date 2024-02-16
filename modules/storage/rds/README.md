# RDS Instance Module

## Description

This module will create a RDS database instance tied to the provided VPC.
The database will also come with automatic credentials rotation for the admin user.

## Inputs/Outputs

### Input Paramenters

#### Required

- `vpc-id`: The ID of the VPC to launch the RDS instance in
- `private-subnet-ids`: Subnet IDs to launch the RDS instance in
- `engine`: database engine (`mysql` or `postgresql`)
- `admin-username`: admin username for the RDS instance

#### Optional

- `instance-type`: instance type for the DB instance
  - defaults to `t2.small`
- `port`: database port
  - if absent, default for the engine will be used
- `multi_az`: whether to launch RDS in MultiAZ mode
  - defaults to `false`
- `removal-policy`: the retention policy to put on the EFS service
  - defaults to `RETAIN`
  - supports `DESTROY` and `RETAIN` only
- `solution-id`: a unique identifier for this deployment (must be used with `solution-description`)
- `solution-name`: a unique name for this deployment (must be used with `solution-id`)
- `solution-version`: a unique version for this deployment

The parameters `(solution-*)` will resolve a custom text that is used as a description of the stack if populated.

### Sample declaration

```yaml
name: mysql
path: modules/storage/rds
targetAccount: primary
parameters:
  - name: vpc-id
    valueFrom:
      moduleMetadata:
        group: networking
        name: basic-networking
        key: VpcId
  - name: private-subnet-ids
    valueFrom:
      moduleMetadata:
        group: networking
        name: basic-networking
        key: PrivateSubnetIds
  - name: engine
    value: mysql
  - name: admin-username
    value: admin
  - name: instance-type
    value: t2.small
  - name: removal-policy
    value: DESTROY
```


### Module Metadata Outputs

- `CredentialsSecretArn`: ARN of the secret
- `DatabaseHostname`: Database hostname
- `DatabasePort`: Database port

#### Output Example

```json
{
    "CredentialsSecretArn": "arn:aws:secretsmanager:*:*:*",
    "DatabaseHostname": "*.*.rds.amazonaws.com",
    "DatabasePort": "3306",
}
```
