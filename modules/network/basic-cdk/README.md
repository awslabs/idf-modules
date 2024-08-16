# Networking Module

## Description

This module creates the below AWS netowrking resources. It may not be required if an end-user already has networking setup in their AWS account(s).

Networking resources are:

  - VPC
  - Public/Private/Isolated Subnets as per the use-case
  - LocalZones
  - Interface/Gateway Endpoints

## Inputs/Outputs

### Input Paramenters

#### Required Paramenters

None

#### Optional

- `vpc-cidr`: You can provide a VPC CIDR to create the AWS VPC with. By default, it creates a VPC with CIDR: `10.0.0.0/16`
- `cidr-mask`: You can configure Subnet CIDR mask to create Subnets. By default, it creates subnets of size: `24`
- `internet-accessible`: a boolean flag indicating whether or not the subnets have internet access. It decides if the module should deploy just the public/private or public/private/isolated subnets with the necessary wiring in place.
  - `true` or `false`
  - Assumed to be True
- `solution-id`: a unique identifier for this deployment (must be used with `solution-description`)
- `solution-name`: a unique name for this deployment (must be used with `solution-id`)
- `solution-version`: a unique version for this deployment
- `local-zones`: List of Local Zones in a given region. Below is an example
> Note: `internet-accessible` should ONLY be set to `true` for deploying local zones.
```json
  name: local-zones
  value: 
    - eu-central-1-ham-1a
```

The parameters `(solution-*)` will resolve a custom text that is used as a description of the stack if populated.

### Module Metadata Outputs

- `VpcId`: The VPC ID created
- `SecurityGroupId`: The Security Group ID created
- `PublicSubnetIds`: An array of the public subnets
- `PrivateSubnetIds`: An array of the private subnets
- `IsolatedSubnetIds`: An array of the isolated subnets  (only if `internet-accessible` is `false`)
- `LocalZonePrivateSubnetIds`: An array of the LocalZone Private subnets
- `LocalZonePublicSubnetIds`: An array of the LocalZone Public subnets

#### Output Example

```json
{ 
  "LocalZonePublicSubnetIds": [],
  "LocalZonePrivateSubnetIds": [],
  "IsolatedSubnetIds": [],
  "PrivateSubnetIds": ["subnet-1234567890abc", "subnet-1234567890def"],
  "PublicSubnetIds": ["subnet-1234567890ghi", "subnet-1234567890jkl"],
  "SecurityGroupId": "sg-123456789abc",
  "VpcId": "vpc-1234567890mno"
}
```
