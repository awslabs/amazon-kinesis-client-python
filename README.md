# Amazon Kinesis Client Library for Python

[![Version](https://img.shields.io/pypi/v/amazon-kclpy.svg?style=flat)](https://pypi.org/project/amazon-kclpy/) [![UnitTestCoverage](https://github.com/awslabs/amazon-kinesis-client-python/actions/workflows/run-unit-tests.yml/badge.svg)](https://github.com/awslabs/amazon-kinesis-client-python/actions/workflows/run-unit-tests.yml)

This package provides an interface to the Amazon Kinesis Client Library (KCL) MultiLangDaemon,
which is part of the [Amazon KCL for Java][kinesis-github].
Developers can use the [Amazon KCL][amazon-kcl] to build distributed applications that
process streaming data reliably at scale. The [Amazon KCL][amazon-kcl] takes care of
many of the complex tasks associated with distributed computing, such as load-balancing
across multiple instances, responding to instance failures, checkpointing processed records,
and reacting to changes in stream volume.
This interface manages the interaction with the MultiLangDaemon so that developers can focus on
implementing their record processor executable. A record processor executable
typically looks something like:

```python
    #!env python
    from amazon_kclpy import kcl
    import json, base64

    class RecordProcessor(kcl.RecordProcessorBase):

        def initialize(self, initialiation_input):
            pass

        def process_records(self, process_records_input):
            pass

        def lease_lost(self, lease_lost_input):
            pass

        def shard_ended(self, shard_ended_input):
            pass

        def shutdown_requested(self, shutdown_requested_input):
            pass

    if __name__ == "__main__":
        kclprocess = kcl.KCLProcess(RecordProcessor())
        kclprocess.run()
```

## Before You Get Started

Before running the samples, you'll want to make sure that your environment is
configured to allow the samples to use your
[AWS Security Credentials](http://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html).

By default the samples use the [DefaultCredentialsProvider][DefaultCredentialsProvider]
so you'll want to make your credentials available to one of the credentials providers in that
provider chain. There are several ways to do this such as providing a ~/.aws/credentials file,
or if you're running on EC2, you can associate an IAM role with your instance with appropriate
access.

For questions regarding Amazon Kinesis Service and the client libraries please visit the
[Amazon Kinesis Forums][kinesis-forum]

## Running the Sample

Using the `amazon_kclpy` package requires the MultiLangDaemon which is provided
by the [Amazon KCL for Java][kinesis-github]. These jars will be downloaded automatically
by the `install` command, but you can explicitly download them with the `download_jars` command.
From the root of this repo, run:

    python setup.py download_jars
    python setup.py install

Now the `amazon_kclpy` and [boto][boto] (used by the sample putter script) and required
jars should be installed in your environment. To start the sample putter, run:

    sample_kinesis_wordputter.py --stream words -w cat -w dog -w bird -w lobster

This will create an Amazon Kinesis stream called words and put the words
specified by the -w options into the stream once each. Use -p SECONDS to
indicate a period over which to repeatedly put these words.

Now we would like to run an Amazon KCL for Python application that reads records
from the stream we just created, but first take a look in the samples directory,
you'll find a file called sample.properties, cat that file:

    cat samples/sample.properties

You'll see several properties defined there. `executableName` indicates the
executable for the MultiLangDaemon to run, `streamName` is the Kinesis stream
to read from, `appName` is the Amazon KCL application name to use which will be the
name of an Amazon DynamoDB table that gets created by the Amazon KCL,
`initialPositionInStream` tells the Amazon KCL how to start reading from shards upon
a fresh startup. To run the sample application you can use a helper script
included in this package. Note you must provide a path to java (version 1.7
or greater) to run the Amazon KCL.

    amazon_kclpy_helper.py --print_command \
        --java <path-to-java> --properties samples/sample.properties

This will print the command needed to run the sample which you can copy paste,
or surround the command with back ticks to run it.

    `amazon_kclpy_helper.py --print_command \
        --java <path-to-java> --properties samples/sample.properties`

Alternatively, if you don't have the source on hand, but want to run the sample
app you can use the `--sample` argument to indicate you'd like to get the
sample.properties file from the installation location.

    amazon_kclpy_helper.py --print_command --java <path-to-java> --sample

## Running on EC2

Running on EC2 is simple. Assuming you are already logged into an EC2 instance running
Amazon Linux, the following steps will prepare your environment for running the sample
app. Note the version of java that ships with Amazon Linux can be found at
`/usr/bin/java` and should be 1.7 or greater.

    sudo yum install python-pip

    sudo pip install virtualenv

    virtualenv /tmp/kclpy-sample-env

    source /tmp/kclpy-sample-env/bin/activate

    pip install amazon_kclpy

## Under the Hood - What You Should Know about Amazon KCL's [MultiLangDaemon][multi-lang-daemon]
Amazon KCL for Python uses [Amazon KCL for Java][kinesis-github] internally. We have implemented
a Java-based daemon, called the *MultiLangDaemon* that does all the heavy lifting. Our approach
has the daemon spawn the user-defined record processor script/program as a sub-process. The
*MultiLangDaemon* communicates with this sub-process over standard input/output using a simple
protocol, and therefore the record processor script/program can be written in any language.

At runtime, there will always be a one-to-one correspondence between a record processor, a child process,
and an [Amazon Kinesis Shard][amazon-kinesis-shard]. The *MultiLangDaemon* will make sure of
that, without any need for the developer to intervene.

In this release, we have abstracted these implementation details away and exposed an interface that enables
you to focus on writing record processing logic in Python. This approach enables [Amazon KCL][amazon-kcl] to
be language agnostic, while providing identical features and similar parallel processing model across
all languages.

## See Also
* [Developing Consumer Applications for Amazon Kinesis Using the Amazon Kinesis Client Library][amazon-kcl]
* The [Amazon KCL for Java][kinesis-github]
* The [Amazon KCL for Ruby][amazon-kinesis-ruby-github]
* The [Amazon Kinesis Documentation][amazon-kinesis-docs]
* The [Amazon Kinesis Forum][kinesis-forum]

## Release Notes

### Release 3.0.0 (November 6, 2024)
* New lease assignment / load balancing algorithm
    * KCL 3.x introduces a new lease assignment and load balancing algorithm. It assigns leases among workers based on worker utilization metrics and throughput on each lease, replacing the previous lease count-based lease assignment algorithm.
    * When KCL detects higher variance in CPU utilization among workers, it proactively reassigns leases from over-utilized workers to under-utilized workers for even load balancing. This ensures even CPU utilization across workers and removes the need to over-provision the stream processing compute hosts.
* Optimized DynamoDB RCU usage
    * KCL 3.x optimizes DynamoDB read capacity unit (RCU) usage on the lease table by implementing a global secondary index with leaseOwner as the partition key. This index mirrors the leaseKey attribute from the base lease table, allowing workers to efficiently discover their assigned leases by querying the index instead of scanning the entire table.
    * This approach significantly reduces read operations compared to earlier KCL versions, where workers performed full table scans, resulting in higher RCU consumption.
* Graceful lease handoff
    * KCL 3.x introduces a feature called "graceful lease handoff" to minimize data reprocessing during lease reassignments. Graceful lease handoff allows the current worker to complete checkpointing of processed records before transferring the lease to another worker. For graceful lease handoff, you should implement checkpointing logic within the existing `shutdownRequested()` method.
    * This feature is enabled by default in KCL 3.x, but you can turn off this feature by adjusting the configuration property `isGracefulLeaseHandoffEnabled`.
    * While this approach significantly reduces the probability of data reprocessing during lease transfers, it doesn't completely eliminate the possibility. To maintain data integrity and consistency, it's crucial to design your downstream consumer applications to be idempotent. This ensures that the application can handle potential duplicate record processing without adverse effects.
* New DynamoDB metadata management artifacts
    * KCL 3.x introduces two new DynamoDB tables for improved lease management:
        * Worker metrics table: Records CPU utilization metrics from each worker. KCL uses these metrics for optimal lease assignments, balancing resource utilization across workers. If CPU utilization metric is not available, KCL assigns leases to balance the total sum of shard throughput per worker instead.
        * Coordinator state table: Stores internal state information for workers. Used to coordinate in-place migration from KCL 2.x to KCL 3.x and leader election among workers.
    * Follow this [documentation](https://docs.aws.amazon.com/streams/latest/dev/kcl-migration-from-2-3.html#kcl-migration-from-2-3-IAM-permissions) to add required IAM permissions for your KCL application.
* Other improvements and changes
    * Dependency on the AWS SDK for Java 1.x has been fully removed.
        * The Glue Schema Registry integration functionality no longer depends on AWS SDK for Java 1.x. Previously, it required this as a transient dependency.
        * Multilangdaemon has been upgraded to use AWS SDK for Java 2.x. It no longer depends on AWS SDK for Java 1.x.
    * `idleTimeBetweenReadsInMillis` (PollingConfig) now has a minimum default value of 200.
        * This polling configuration property determines the [publishers](https://github.com/awslabs/amazon-kinesis-client/blob/master/amazon-kinesis-client/src/main/java/software/amazon/kinesis/retrieval/polling/PrefetchRecordsPublisher.java) wait time between GetRecords calls in both success and failure cases. Previously, setting this value below 200 caused unnecessary throttling. This is because Amazon Kinesis Data Streams supports up to five read transactions per second per shard for shared-throughput consumers.
    * Shard lifecycle management is improved to deal with edge cases around shard splits and merges to ensure records continue being processed as expected.
* Migration
    * The programming interfaces of KCL 3.x remain identical with KCL 2.x for an easier migration. For detailed migration instructions, please refer to the [Migrate consumers from KCL 2.x to KCL 3.x](https://docs.aws.amazon.com/streams/latest/dev/kcl-migration-from-2-3.html) page in the Amazon Kinesis Data Streams developer guide.
* Configuration properties
    * New configuration properties introduced in KCL 3.x are listed in this [doc](https://github.com/awslabs/amazon-kinesis-client/blob/master/docs/kcl-configurations.md#new-configurations-in-kcl-3x).
    * Deprecated configuration properties in KCL 3.x are listed in this [doc](https://github.com/awslabs/amazon-kinesis-client/blob/master/docs/kcl-configurations.md#discontinued-configuration-properties-in-kcl-3x). You need to keep the deprecated configuration properties during the migration from any previous KCL version to KCL 3.x.
* Metrics
    * New CloudWatch metrics introduced in KCL 3.x are explained in the [Monitor the Kinesis Client Library with Amazon CloudWatch](https://docs.aws.amazon.com/streams/latest/dev/monitoring-with-kcl.html) in the Amazon Kinesis Data Streams developer guide. The following operations are newly added in KCL 3.x:
        * `LeaseAssignmentManager`
        * `WorkerMetricStatsReporter`
        * `LeaseDiscovery`
---
For **2.x** and **1.x** release notes, please see [v2.x/README.md](https://github.com/awslabs/amazon-kinesis-client-python/blob/v2.x/README.md#release-notes)

[amazon-kinesis-shard]: http://docs.aws.amazon.com/kinesis/latest/dev/key-concepts.html
[amazon-kinesis-docs]: http://aws.amazon.com/documentation/kinesis/
[amazon-kcl]: http://docs.aws.amazon.com/kinesis/latest/dev/kinesis-record-processor-app.html
[multi-lang-daemon]: https://github.com/awslabs/amazon-kinesis-client/blob/master/src/main/java/com/amazonaws/services/kinesis/multilang/package-info.java
[kinesis]: http://aws.amazon.com/kinesis
[amazon-kinesis-ruby-github]: https://github.com/awslabs/amazon-kinesis-client-ruby
[kinesis-github]: https://github.com/awslabs/amazon-kinesis-client
[boto]: http://boto.readthedocs.org/en/latest/
[DefaultCredentialsProvider]: https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/auth/credentials/DefaultCredentialsProvider.html
[kinesis-forum]: http://developer.amazonwebservices.com/connect/forum.jspa?forumID=169

## License

This library is licensed under the Apache 2.0 License.
