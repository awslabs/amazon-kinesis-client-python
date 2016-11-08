.. _guide_sample:

Running the Sample Application
==============================
The sample application provided with this module shows the basics of using the Amazon Kinesis Client for Python.

Before Getting Started
----------------------
Before running the samples, you'll want to make sure that your environment is
configured to allow the samples to use your
`AWS Security Credentials <http://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html>`_.

By default the samples use the `DefaultAWSCredentialsProviderChain <http://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/auth/DefaultAWSCredentialsProviderChain.html>`_
so you'll want to make your credentials available to one of the credentials providers in that
provider chain. There are several ways to do this such as providing a ~/.aws/credentials file,
or if you're running on EC2, you can associate an IAM role with your instance with appropriate
access.

For questions regarding Amazon Kinesis Service and the client libraries please visit the
`Amazon Kinesis Forums <http://developer.amazonwebservices.com/connect/forum.jspa?forumID=169>`_

Running the Sample
------------------

Using the ``amazon_kclpy`` package requires the MultiLangDaemon which is provided
by the `Amazon KCL for Java <https://github.com/awslabs/amazon-kinesis-client>`. These jars will be downloaded automatically
by the **install** command, but you can explicitly download them with the ``download_jars`` command.
From the root of this repo, run::

    python setup.py download_jars
    python setup.py install

Now the ``amazon_kclpy`` and `boto < http://boto.readthedocs.org/en/latest/>`_ (used by the sample putter script) and required
jars should be installed in your environment. To start the sample putter, run::

    sample_kinesis_wordputter.py --stream words -w cat -w dog -w bird -w lobster

This will create an Amazon Kinesis stream called words and put the words
specified by the -w options into the stream once each. Use -p SECONDS to
indicate a period over which to repeatedly put these words.

Now we would like to run an Amazon KCL for Python application that reads records
from the stream we just created, but first take a look in the samples directory,
you'll find a file called sample.properties, cat that file::

    cat samples/sample.properties

You'll see several properties defined there. ``executableName`` indicates the
executable for the MultiLangDaemon to run, ``streamName`` is the Kinesis stream
to read from, ``appName`` is the Amazon KCL application name to use which will be the
name of an Amazon DynamoDB table that gets created by the Amazon KCL,
``initialPositionInStream`` tells the Amazon KCL how to start reading from shards upon
a fresh startup. To run the sample application you can use a helper script
included in this package. Note you must provide a path to java (version 1.7
or greater) to run the Amazon KCL::

    amazon_kclpy_helper.py --print_command \
        --java <path-to-java> --properties samples/sample.properties

This will print the command needed to run the sample which you can copy paste,
or surround the command with back ticks to run it::

    `amazon_kclpy_helper.py --print_command \
        --java <path-to-java> --properties samples/sample.properties`

Alternatively, if you don't have the source on hand, but want to run the sample
app you can use the ``--sample`` argument to indicate you'd like to get the
sample.properties file from the installation location::

    amazon_kclpy_helper.py --print_command --java <path-to-java> --sample

The Sample Code
---------------
.. autoclass:: samples.sample_kclpy_app.RecordProcessor
    :members:
