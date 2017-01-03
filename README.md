# Amazon Kinesis Client Library for Python

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

        def initialize(self, shard_id):
            pass

        def process_records(self, records, checkpointer):
            pass

        def shutdown(self, checkpointer, reason):
            pass

    if __name__ == "__main__":
        kclprocess = kcl.KCLProcess(RecordProcessor())
        kclprocess.run()
```

## Before You Get Started

Before running the samples, you'll want to make sure that your environment is
configured to allow the samples to use your
[AWS Security Credentials](http://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html).

By default the samples use the [DefaultAWSCredentialsProviderChain][DefaultAWSCredentialsProviderChain]
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
[DefaultAWSCredentialsProviderChain]: http://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/auth/DefaultAWSCredentialsProviderChain.html
[kinesis-forum]: http://developer.amazonwebservices.com/connect/forum.jspa?forumID=169
