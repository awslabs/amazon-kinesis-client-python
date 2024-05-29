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

### Release 2.1.5 (May 29, 2024)
* Fixed CI due to different macOS architecture [PR #246](https://github.com/awslabs/amazon-kinesis-client-python/pull/246)
* Added necessary Java SDKs to run sample [PR #248](https://github.com/awslabs/amazon-kinesis-client-python/pull/248)
* Upgraded boto dependency to boto3 [PR #245](https://github.com/awslabs/amazon-kinesis-client-python/pull/245)
* Upgraded AWS SDK from 2.19.2 to 2.25.11 [PR #248](https://github.com/awslabs/amazon-kinesis-client-python/pull/248)
* Upgraded aws-java-sdk from 1.12.370 to 1.12.668 [PR #248](https://github.com/awslabs/amazon-kinesis-client-python/pull/248)

### Release 2.1.4 (April 23, 2024)
* Upgraded KCL and KCL-Multilang dependencies from 2.5.2 to 2.5.8 [PR #239](https://github.com/awslabs/amazon-kinesis-client-python/pull/239)
* Upgraded ion-java from 1.5.1 to 1.11.4 [PR #243](https://github.com/awslabs/amazon-kinesis-client-python/pull/243)
* Upgraded logback version from 1.3.0 to 1.3.12 [PR #242](https://github.com/awslabs/amazon-kinesis-client-python/pull/242)
* Upgraded io.netty dependency from 4.1.86.Final to 4.1.94.Final [PR #234](https://github.com/awslabs/amazon-kinesis-client-python/pull/234)
* Upgraded Google Guava dependency from 32.0.0-jre to 32.1.1-jre [PR #234](https://github.com/awslabs/amazon-kinesis-client-python/pull/234)
* Upgraded jackson-databind from 2.13.4 to 2.13.5 [PR #234](https://github.com/awslabs/amazon-kinesis-client-python/pull/234)
* Upgraded protobuf-java from 3.21.5 to 3.21.7 [PR #234](https://github.com/awslabs/amazon-kinesis-client-python/pull/234)

### Release 2.1.3 (August 8, 2023)
* Added the ability to specify STS endpoint and region [PR #221](https://github.com/awslabs/amazon-kinesis-client-python/pull/230)
* Upgraded KCL and KCL-Multilang Dependencies from 2.5.1 to 2.5.2 [PR #221](https://github.com/awslabs/amazon-kinesis-client-python/pull/230)

### Release 2.1.2 (June 29, 2023)
* Added the ability to pass in streamArn to multilang Daemon [PR #221](https://github.com/awslabs/amazon-kinesis-client-python/pull/221)
* Upgraded KCL and KCL-Multilang Dependencies from 2.4.4 to 2.5.1 [PR #221](https://github.com/awslabs/amazon-kinesis-client-python/pull/221)
* Upgraded Google Guava dependency from 31.0.1-jre to 32.0.0-jre [PR #223](https://github.com/awslabs/amazon-kinesis-client-python/pull/223)
* Added aws-java-sdk-sts dependency [PR #212](https://github.com/awslabs/amazon-kinesis-client-python/pull/212)

### Release 2.1.1 (January 17, 2023)
* Include the pom file in MANIFEST

### Release 2.1.0 (January 12, 2023)
* Upgraded to use version 2.4.4 of the [Amazon Kinesis Client library][kinesis-github]

### Release 2.0.6 (November 23, 2021)
* Upgraded multiple dependencies [PR #152](https://github.com/awslabs/amazon-kinesis-client-python/pull/152)
  * Amazon Kinesis Client Library 2.3.9
  * ch.qos.logback 1.2.7

### Release 2.0.5 (November 11, 2021)
* Upgraded multiple dependencies [PR #148](https://github.com/awslabs/amazon-kinesis-client-python/pull/148)
  * Amazon Kinesis Client Library 2.3.8
  * AWS SDK 2.17.52
* Added dependencies 
  * AWS SDK json-utils 2.17.52
  * third-party-jackson-core 2.17.52
  * third-party-jackson-dataformat-cbor 2.17.52
* Updated samples/sample.properties reflecting support for InitialPositionInStreamExtended
  * Related: [#804](https://github.com/awslabs/amazon-kinesis-client/pull/804) Allowing user to specify an initial timestamp in which daemon will process records.
  * Feature released with previous [release 2.0.4](https://github.com/awslabs/amazon-kinesis-client-python/releases/tag/v2.0.4)

### Release 2.0.4 (October 26, 2021) 
* Revert/downgrade multiple dependencies as KCL 2.3.7 contains breaking change [PR #145](https://github.com/awslabs/amazon-kinesis-client-python/pull/145)
  * Amazon Kinesis Client Library 2.3.6
  * AWS SDK 2.16.98
* Upgraded dependencies
  * jackson-dataformat-cbor 2.12.4
  * AWS SDK 1.12.3

### :warning: [BREAKING CHANGES] Release 2.0.3 (October 21, 2021)
* Upgraded multiple dependencies in [PR #142](https://github.com/awslabs/amazon-kinesis-client-python/pull/142)
  * Amazon Kinesis Client Library 2.3.7
  * AWS SDK 2.17.52
  * AWS Java SDK 1.12.1
  * AWS Glue 1.1.5
  * Jackson 2.12.4
  * io.netty 4.1.68.Final
  * guava 31.0.1-jre

### Release 2.0.2 (June 4, 2021)
* Upgraded multiple dependencies in [PR #137](https://github.com/awslabs/amazon-kinesis-client-python/pull/137)
  * Amazon Kinesis Client Library 2.3.4
  * AWS SDK 2.16.75
  * AWS Java SDK 1.11.1031
  * Amazon ion java 1.5.1
  * Jackson 2.12.3
  * io.netty 4.1.65.Final
  * typeface netty 2.0.5
  * reactivestreams 1.0.3
  * guava 30.1.1-jre
  * Error prone annotations 2.7.1
  * j2objc annotations 2.7.1
  * Animal sniffer annotations 1.20
  * slf4j 1.7.30
  * protobuf 3.17.1
  * Joda time 2.10.10
  * Apache httpclient 4.5.13
  * Apache httpcore 4.4.14
  * commons lang3 3.12.0
  * commons logging 1.2
  * commons beanutils 1.9.4
  * commons codec 1.15
  * commons collections4 4.4
  * commons io 2.9.0
  * jcommander 1.81
  * rxjava 2.2.21
* Added Amazon Glue schema registry 1.0.2

### Release 2.0.1 (February 27, 2019)
* Updated to version 2.1.2 of the Amazon Kinesis Client Library for Java.  
  This update also includes version 2.4.0 of the AWS Java SDK.
  * [PR #92](https://github.com/awslabs/amazon-kinesis-client-python/pull/92)

### Release 2.0.0 (January 15, 2019)
* Introducing support for Enhanced Fan-Out
* Updated to version 2.1.0 of the Amazon Kinesis Client for Java
  * Version 2.1.0 now defaults to using [`RegisterStreamConsumer` Kinesis API](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_RegisterStreamConsumer.html), which provides dedicated throughput compared to `GetRecords`.
  * Version 2.1.0 now defaults to using [`SubscribeToShard` Kinesis API](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_SubscribeToShard.html), which provides lower latencies than `GetRecords`.
  * __WARNING: `RegisterStreamConsumer` and `SubscribeToShard` are new APIs, and may require updating any explicit IAM policies__
  * For more information about Enhaced Fan-Out and Polling with the KCL check out the [announcement](https://aws.amazon.com/blogs/aws/kds-enhanced-fanout/) and [developer documentation](https://docs.aws.amazon.com/streams/latest/dev/introduction-to-enhanced-consumers.html).
* Introducing version 3 of the `RecordProcessorBase` which supports the new `ShardRecordProcessor` interface
  * The `shutdown` method from version 2 has been removed and replaced by `leaseLost` and `shardEnded` methods.
  * Introducing `leaseLost` method, which takes `LeaseLostInput` object and is invoked when a lease is lost.
  * Introducing `shardEnded` method, which takes `ShardEndedInput` object and is invoked when all records from a split/merge have been processed.
* Updated AWS SDK version to 2.2.0
* MultiLangDaemon now uses logging using logback
  * MultiLangDaemon supports custom logback.xml file via the `--log-configuration` option.
  * `amazon_kclpy_helper` script supports `--log-configuration` option for command generation.

### Release 1.5.1 (January 2, 2019)
* Updated to version 1.9.3 of the Amazon Kinesis Client Library for Java.
  * [PR #87](https://github.com/awslabs/amazon-kinesis-client-python/pull/87)
* Changed to now download jars from Maven using https.
  * [PR #87](https://github.com/awslabs/amazon-kinesis-client-python/pull/87)
* Changed to raise exception when downloading from Maven fails.
  * [PR #80](https://github.com/awslabs/amazon-kinesis-client-python/pull/80)

### Release 1.5.0 (February 7, 2018)
* Updated to version 1.9.0 of the Amazon Kinesis Client Library for Java
  * Version 1.9.0 now uses the [`ListShards` Kinesis API](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_ListShards.html), which provides a higher call rate than `DescribeStream`.
  * __WARNING: `ListShards` is a new API, and may require updating any explicit IAM policies__
  * [PR #71](https://github.com/awslabs/amazon-kinesis-client-python/pull/71)

### Release 1.4.5 (June 28, 2017)
* Record processors can now be notified, and given a final opportunity to checkpoint, when the KCL is being shutdown.
  * [PR #53](https://github.com/awslabs/amazon-kinesis-client-python/pull/53)
  * [PR #56](https://github.com/awslabs/amazon-kinesis-client-python/pull/56)
  * [PR #57](https://github.com/awslabs/amazon-kinesis-client-python/pull/57)

  To use this feature the record processor must implement the `shutdown_requested` operation from the respective processor module.
  See [v2/processor.py](https://github.com/awslabs/amazon-kinesis-client-python/blob/master/amazon_kclpy/v2/processor.py#L76) or [kcl.py](https://github.com/awslabs/amazon-kinesis-client-python/blob/master/amazon_kclpy/kcl.py#L223) for the required API.

### Release 1.4.4 (April 7, 2017)
* [PR #47](https://github.com/awslabs/amazon-kinesis-client-python/pull/47): Update to release 1.7.5 of the Amazon Kinesis Client.
  * Additionally updated to version 1.11.115 of the AWS Java SDK.
  * Fixes [Issue #43](https://github.com/awslabs/amazon-kinesis-client-python/issues/43).
  * Fixes [Issue #27](https://github.com/awslabs/amazon-kinesis-client-python/issues/27).

### Release 1.4.3 (January 3, 2017)
* [PR #39](https://github.com/awslabs/amazon-kinesis-client-python/pull/39): Make record objects subscriptable for backwards compatibility.

### Release 1.4.2 (November 21, 2016)
* [PR #35](https://github.com/awslabs/amazon-kinesis-client-python/pull/35): Downloading JAR files now runs correctly.

### Release 1.4.1 (November 18, 2016)
* Installation of the library into a virtual environment on macOS, and Windows now correctly downloads the jar files.
  * Fixes [Issue #33](https://github.com/awslabs/amazon-kinesis-client-python/issues/33)

### Release 1.4.0 (November 9, 2016)
* Added a new v2 record processor class that allows access to updated features.
  * Record processor initialization
    * The initialize method receives an InitializeInput object that provides shard id, and the starting sequence and sub sequence numbers.
  * Process records calls
    * The process_records calls now receives a ProcessRecordsInput object that, in addition to the records, now includes the millisBehindLatest for the batch of records
    * Records are now represented as a Record object that adds new data, and includes some convenience methods
      * Adds a `binary_data` method that handles the base 64 decode of the data.
      * Includes the sub sequence number of the record.
      * Includes the approximate arrival time stamp of the record.
  * Record processor shutdown
    * The method `shutdown` now receives a `ShutdownInput` object.
* Checkpoint methods now accept a sub sequence number in addition to the sequence number.

### Release 1.3.1
* Version number increase to stay inline with PyPI.

### Release 1.3.0
* Updated dependency to Amazon KCL version 1.6.4

### Release 1.2.0
* Updated dependency to Amazon KCL version 1.6.1

### Release 1.1.0 (January 27, 2015)
* **Python 3 support** All Python files are compatible with Python 3

### Release 1.0.0 (October 21, 2014)
* **amazon_kclpy** module exposes an interface to allow implementation of record processor executables that are compatible with the MultiLangDaemon
* **samples** module provides a sample putter application using [boto][boto] and a sample processing app using `amazon_kclpy`

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
