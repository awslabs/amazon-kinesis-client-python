'''
Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0


BEFORE YOU GET STARTED
======================

Before running the samples, you'll want to make sure that your environment is
configured to allow the samples to use your AWS credentials. To familiarize
yourself with AWS Credentials read this guide:

    http://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html

For the MultiLangDaemon and boto libs you'll want to make your credentials 
available to one of the credentials providers in the default credential
providers chain such as providing a ~/.aws/credentials file 

    http://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/auth/DefaultAWSCredentialsProviderChain.html

RUNNING THE SAMPLE
==================

Navigate to the amazon_kclpy directory and install the package. Using the amazon_kclpy
package requires the MultiLangDaemon which is provided by the java KCL. To get
the necessary jars to this directory before installing, you'll want to run the
"download_jars" command before running "install". If you just want the python
KCL and plan to retrieve the necessary jars yourself, you can just do "install"

    python setup.py download_jars
    python setup.py install

Now the amazon_kclpy and boto and required jars should be installed in your
environment. To start the sample putter, run:

    sample_kinesis_wordputter.py --stream words -w cat -w dog -w bird

This will create a Kinesis stream called words and put the words specified by
the -w options into the stream once each. Use -p SECONDS to indicate a period
over which to repeatedly put these words.

Now we would like to run a python KCL application that reads records from
the stream we just created, but first take a look in the samples directory,
you'll find a file called sample.properties, cat that file:

    cat samples/sample.properties

You'll see several properties defined there. "executableName" indicates the
executable for the MultiLangDaemon to run, "streamName" is the Kinesis stream
to read from, "appName" is the KCL application name to use which will be the
name of a DynamoDB table that gets created by the KCL, "initialPositionInStream"
tells the KCL how to start reading from shards upon a fresh startup. To run the
sample application you can use a helper script included in the package.

    amazon_kclpy_helper.py --print_command \
        --java <path-to-java> --properties samples/sample.properties

This will print the command needed to run the sample which you can copy paste,
or surround the command with back ticks, e.g.

    `amazon_kclpy_helper.py --print_command \
        --java <path-to-java> --properties samples/sample.properties`
'''
