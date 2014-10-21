# Amazon Kinesis Client Library for Python

This package provides an interface to the KCL MultiLangDaemon, which is part of the
[Amazon Kinesis Client Library][kinesis-github]. This interface manages the
interaction with the MultiLangDaemon so that developers can focus on
implementing their record processor executable. A record processor executable
typically looks something like:

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
by the java KCL. These jars will be downloaded automatically by the `install`
command, but you can explicitly download them with the `download_jars` command.
From the root of this repo, run:

    python setup.py download_jars
    python setup.py install

Now the `amazon_kclpy` and [boto][boto] (used by the sample putter script) and required
jars should be installed in your environment. To start the sample putter, run:

    sample_kinesis_wordputter.py --stream words -w cat -w dog -w bird -w lobster

This will create an Amazon Kinesis stream called words and put the words
specified by the -w options into the stream once each. Use -p SECONDS to
indicate a period over which to repeatedly put these words.

Now we would like to run a python KCL application that reads records from
the stream we just created, but first take a look in the samples directory,
you'll find a file called sample.properties, cat that file:

    cat samples/sample.properties

You'll see several properties defined there. `executableName` indicates the
executable for the MultiLangDaemon to run, `streamName` is the Kinesis stream
to read from, `appName` is the KCL application name to use which will be the
name of an Amazon DynamoDB table that gets created by the KCL,
`initialPositionInStream` tells the KCL how to start reading from shards upon
a fresh startup. To run the sample application you can use a helper script
included in this package. Note you must provide a path to java (version 1.7
or greater) to run the KCL.

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

## Release Notes
### Release 1.0.0 (October 21, 2014)
* **amazon_kclpy** module exposes an interface to allow implementation of record processor executables that are compatible with the MultiLangDaemon
* **samples** module provides a sample putter application using [boto][boto] and a sample processing app using `amazon_kclpy`

[kinesis]: http://aws.amazon.com/kinesis
[kinesis-github]: https://github.com/awslabs/amazon-kinesis-client
[boto]: http://boto.readthedocs.org/en/latest/
[DefaultAWSCredentialsProviderChain]: http://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/auth/DefaultAWSCredentialsProviderChain.html
[kinesis-forum]: http://developer.amazonwebservices.com/connect/forum.jspa?forumID=169
