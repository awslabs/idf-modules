# RDS Instance Module

## Description

This module will create a RDS database instance tied to the provided VPC.
The password for the database admin will be automatically generated and stored in SecretsManager.
The module can also set up SecretsManager to automatically rotate the credentials.

## Inputs/Outputs

### Input Paramenters

#### Required

- `vpc-id`: the ID of the VPC to launch the RDS instance in
- `private-subnet-ids`: Subnet IDs to launch the RDS instance in
- `database-name`: Name of the database
- `engine`: database engine (`mysql` or `postgresql`)
- `engine-version`: engine version
- `admin-username`: admin username for the RDS instance

#### Optional

- `instance-type`: instance type for the DB instance
  - defaults to `t2.small`
- `credential-rotation-days`: schedule for the credential rotation in days
  - if absent, no rotation will be set up
  - the value can also explicitely be set to 0 to remove the rotation
- `port`: database port
  - if absent, default for the engine will be used
- `accessible-from-vpc`: whether a rule will be added to the RDS security group which will allow all inbound connections from the VPC
  - defaults to `false`
  - if `false`, any consumers of this module will need to modify the RDS instance's security group to add an inbound rule
- `removal-policy`: the retention policy to put on the RDS instance
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
  - name: engine-version
    value: 8.0.35
  - name: instance-type
    value: t2.small
  - name: admin-username
    value: admin
  - name: credential-rotation-days
    value: 30
  - name: removal-policy
    value: DESTROY
```


### Module Metadata Outputs

- `CredentialsSecretArn`: ARN of the secret
- `DatabaseHostname`: Database hostname
- `DatabasePort`: Database port
- `SecurityGroupId`: ID of the database security group

#### Output Example

```json
{
    "CredentialsSecretArn": "arn:aws:secretsmanager:*:*:*",
    "DatabaseHostname": "*.*.rds.amazonaws.com",
    "DatabasePort": "3306",
    "SecurityGroupId": "sg-061e67210cc11f841",
}
```
