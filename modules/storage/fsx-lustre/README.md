## Introduction

FSx on Lustre

## Description

Amazon FSx for Lustre provides fully managed shared storage with the scalability and performance of the popular Lustre file system.

Amazon FSx also integrates with Amazon S3, making it easy for you to process cloud data sets with the Lustre high-performance file system. When linked to an S3 bucket, an FSx for Lustre file system transparently presents S3 objects as files and automatically updates the contents of the linked S3 bucket as files are added to, changed in, or deleted from the file system.

Amazon FSx for Lustre uses parallel data transfer techniques to transfer data to and from S3 at up to hundreds of GB/s. Use Amazon FSx for Lustre for workloads where speed matters.

### WARNING

Currently, this module is only tested for FSX Lustre mode only.

## Inputs/Outputs

Amazon FSx for Lustre provides two deployment options: `scratch` and `persistent`.

Scratch file systems are designed for temporary storage and shorter-term processing of data. You can configure data replication between FSX and S3 bucket using [Data repository association](https://docs.aws.amazon.com/fsx/latest/LustreGuide/create-dra-linked-data-repo.html) only with `SCRATCH_2` deployment type.

Persistent file systems are designed for longer-term storage and workloads. The file servers are highly available, and data is automatically replicated within the AWS Availability Zone (AZ) that is associated with the file system. The data volumes attached to the file servers are replicated independently from the file servers to which they are attached. You can configure data replication between FSX and S3 bucket using [Data repository association](https://docs.aws.amazon.com/fsx/latest/LustreGuide/create-dra-linked-data-repo.html) only with `PERSISTENT_2` deployment type.

### Input Parameters

#### Required

- `vpc_id`: The VPC in which to create the security group for your file system
- `private_subnet_ids`: Specifies the IDs of the subnets that the file system will be accessible from
- `fs_deployment_type`:
  - Choose `SCRATCH_1` and `SCRATCH_2` deployment types when you need temporary storage and shorter-term processing of data. The `SCRATCH_2` deployment type provides in-transit encryption of data and higher burst throughput capacity than `SCRATCH_1` .
  - Choose `PERSISTENT_1` for longer-term storage and for throughput-focused workloads that aren’t latency-sensitive. `PERSISTENT_1` supports encryption of data in transit, and is available in all AWS Regions in which FSx for Lustre is available.
  - Choose `PERSISTENT_2` for longer-term storage and for latency-sensitive workloads that require the highest levels of IOPS/throughput. `PERSISTENT_2` supports SSD storage, and offers higher PerUnitStorageThroughput (up to 1000 MB/s/TiB). `PERSISTENT_2` is available in a limited number of AWS Regions.
  - For more information, and an up-to-date list of AWS Regions in which `PERSISTENT_2` is available, see File system deployment options for FSx for Lustre in the Amazon FSx for Lustre User Guide . .. epigraph:: If you choose `PERSISTENT_2` , and you set FileSystemTypeVersion to 2.10, the CreateFileSystem operation fails. Encryption of data in transit is automatically turned on when you access SCRATCH_2 , PERSISTENT_1 and `PERSISTENT_2` file systems from Amazon EC2 instances that [support automatic encryption](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/data- protection.html) in the AWS Regions where they are available. For more information about encryption in transit for FSx for Lustre file systems, see Encrypting data in transit in the Amazon FSx for Lustre User Guide . (Default = SCRATCH_1 )

#### Optional

- `fsx_version`: The version of FSX-Luster to use (`2.10`,`2.12`,`2.15`)
  - defaults to `2.12`
- `data_bucket_name`: The S3 bucket used for mapping to and from the FSx filesystem
- `export_path`: Available with `Scratch` and `Persistent_1` deployment types. Specifies the path in the Amazon S3 bucket where the root of your Amazon FSx file system is exported. The path will use the same Amazon S3 bucket as specified in `data_bucket_name`. You can provide an optional prefix to which new and changed data is to be exported from your Amazon FSx for Lustre file system. If an ExportPath value is not provided, Amazon FSx sets a default export path, s3://import-bucket/FSxLustre[creation-timestamp] . The timestamp is in UTC format, for example s3://import-bucket/FSxLustre20181105T222312Z . The Amazon S3 export bucket must be the same as the import bucket specified by ImportPath . If you specify only a bucket name, such as s3://import-bucket, you get a 1:1 mapping of file system objects to S3 bucket objects. This mapping means that the input data in S3 is overwritten on export. If you provide a custom prefix in the export path, such as s3://import-bucket/[custom-optional-prefix] , Amazon FSx exports the contents of your file system to that export prefix in the Amazon S3 bucket.
  - This parameter is not supported for file systems using the `Persistent_2` deployment type in version `2.10`.
- `import_path`: The path to the Amazon S3 bucket that you’re using as the data repository for your Amazon FSx for Lustre file system. The root of your FSx for Lustre file system will be mapped to the root of the Amazon S3 bucket you select. If you specify a prefix for the Amazon S3 bucket name, only object keys with that prefix are loaded into the file system.
  - This parameter is not supported for Lustre file systems using the Persistent_2 deployment type in version `2.10`.
- `dra_import_path`: Configure it when you want to link a specific path in your filesystem with S3 bucket, where you can import all the change(s) made on S3 onto the filesystem using Data repository assoociation. Must start with a `/`.
- `dra_export_path`: Configure it when you want to link a specific path in your filesystem with S3 bucket, where you can import all the change(s) made on the filesystem onto S3 bucket using Data repository assoociation. Must start with a `/`.
- `storage_throughput`: Required with `PERSISTENT_1` and `PERSISTENT_2` deployment types, provisions the amount of read and write throughput for each 1 tebibyte (TiB) of file system storage capacity, in MB/s/TiB. File system throughput capacity is calculated by multiplying ﬁle system storage capacity (TiB) by the PerUnitStorageThroughput (MB/s/TiB). For a 2.4-TiB ﬁle system, provisioning 50 MB/s/TiB of PerUnitStorageThroughput yields 120 MB/s of ﬁle system throughput. You pay for the amount of throughput that you provision.
  - For `PERSISTENT_1` SSD storage: 50, 100, 200 MB/s/TiB.
  - For `PERSISTENT_1` HDD storage: 12, 40 MB/s/TiB.
  - For `PERSISTENT_2` SSD storage: 125, 250, 500, 1000 MB/s/TiB.
- `storage_capacity`: the amount (in GB) of storage for a newly created filesystem, **defaults to 1200**, with the following guidelines:
  - For `SCRATCH_2` , `PERSISTENT_2` and `PERSISTENT_1`  the valid values are 1200 GiB, 2400 GiB, and increments of 2400 GiB
  - For `SCRATCH_1` valid values are 1200 GiB, 2400 GiB, and increments of 3600 GiB.
- `import_policy` - must be one of `NEW`or `NEW_CHANGED` or `NEW_CHANGED_DELETED`
  - this does not support types of `SCRATCH_1`

> Note: You should not declare `import_path` and `export_path` if you have declared `dra_import_path` and `dra_export_path`. It is recommended to use `dra_import_path` and `dra_export_path` since they help with establishing association between FSX and S3 bucket bi-directionally.

### Input Example

Stand-alone module manifest example:

```yaml
name: storage
path: modules/core/fsx-lustre/
parameters:
  - name: private_subnet_ids
    value: [subnet-abc1234]
  - name: vpc_id
    value: vpc-123abc34
  - name: data_bucket_name
    value: data_bucket_name
  - name: fs_deployment_type
    value: PERSISTENT_2
  - name: storage_throughput
    value: 125
  # - name: export_path
  #   value: "/fsx/export/"
  # - name: import_path
  #   value: "/fsx/import/"
  - name: dra_export_path # Do not mention import_path and export_path if you mention dra_export_path and dra_import_path
    value: "/ray/export/"
  - name: dra_import_path
    value: "/ray/import/"
  - name: fsx_version 
    value: "2.15"
  - name: import_policy
    value: "NEW_CHANGED_DELETED"
  - name: storage_capacity
    value: 1200
```

Module manifest leveraging the `networking` module:

```yaml
name: storage
path: modules/core/fsx-lustre/
parameters:
  - name: private_subnet_ids
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: PrivateSubnetIds
  - name: vpc_id
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: VpcId
  ...
```

### Module Metadata Outputs

#### Output Example

```json
{
  "FSxLustreAttrDnsName": "fs-05d205d87c763d71e.fsx.us-east-1.amazonaws.com",
  "FSxLustreFileSystemDeploymentType": "PERSISTENT_2",
  "FSxLustreFileSystemId": "fs-05d205d87c763d71e",
  "FSxLustreMountName": "frinzbev",
  "FSxLustreSecurityGroup": "sg-0ca5da2aebca3459b",
  "FSxLustreVersion": "2.15",
  "FSxLustreStorageCapacity": 1200
}
```
