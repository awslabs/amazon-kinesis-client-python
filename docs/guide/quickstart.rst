.. _guide_quickstart:

Getting Started Using the Amazon Kinesis Client for Python
==========================================================
This assumes you're already publishing data to Kinesis.  If you're not publishing see :doc:`sample`.  In
addition you will need to ensure that you have a Java Runtime Environment (JRE) installed.  The JRE must be version
1.7 or greater.

Prerequisites
-------------
There are a few prerequisites for using the Amazon Kinesis Client for Python.

Publishing Data to Kinesis
^^^^^^^^^^^^^^^^^^^^^^^^^^

You must have an AWS Account, and be publishing some data to Kinesis that you intend to process.
If you're not publishing you can use the sample publisher described in the :doc:`sample`.

Install a Java Runtime Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You must have a Java Runtime Environment (JRE) version 1.7 or greater installed.  It's recommended you use the newest
version of the JRE, which is currently 1.8

To install the 1.8 version of the JRE on Amazon Linux you can run the following command::

    sudo yum install java-1.8.0-openjdk.x86_64

For other operating systems please refer to your system's documentation.

It is also possible to download, and install a JRE from Oracle `Java SE Runtime Environment 8 <http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html>`_


Installing the Amazon Kinesis Client for Python
-----------------------------------------------
The first thing to do is install the Amazon Kinesis Client for Python (KCL).  You can install the KCL from pip using::

    pip install amazon_kclpy

This should install the KCL, and automatically download the necessary jars.


Create A Record Processor
-------------------------
The record processor is how the KCL will communicate with your application.  Create a file with a class that extends
:class:`amazon_kclpy.v2.processor.RecordProcessorBase`.  See the :doc:`sample` for an example of a record processor.

Create A Properties File
------------------------
The KCL uses a Java properties file to configure itself.  The Java process uses this file to configure the KCL, and
determine which python script to run for record processing.  See the
:download:`sample.properties <../../samples/sample.properties>` for documentation, and required values.

Create the Startup Command
--------------------------
The KCL includes a script to help generate the command line to start the KCL application.  TO create the startup
command for your application use::

    amazon_kclpy_helper.py --print_command \
            --java <path-to-java> --properties <path to your properties file>

.. automodule:: samples.amazon_kclpy_helper
    :special-members:




