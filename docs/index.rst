.. Amazon Kinesis Client Library for Python documentation master file, created by
sphinx-quickstart on Mon Oct 24 12:24:53 2016.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive.

Amazon Kinesis Client Library for Python
========================================
This package provides an interface to the Amazon Kinesis Client Library (KCL) MultiLangDaemon,
which is part of the `Amazon KCL for Java <https://github.com/awslabs/amazon-kinesis-client>`_.
Developers can use the `Amazon KCL <http://docs.aws.amazon.com/kinesis/latest/dev/kinesis-record-processor-app.html>`_
to build distributed applications that process streaming data reliably at scale. The
`Amazon KCL <http://docs.aws.amazon.com/kinesis/latest/dev/kinesis-record-processor-app.html>`_
takes care of many of the complex tasks associated with distributed computing, such as load-balancing
across multiple instances, responding to instance failures, checkpointing processed records,
and reacting to changes in stream volume.
This interface manages the interaction with the MultiLangDaemon so that developers can focus on
implementing their record processor executable. A record processor executable
typically looks something like:


Guides
------

.. toctree::
   :maxdepth: 2

   guide/quickstart
   guide/sample
   guide/record_processor_v1
   guide/record_processor_v2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

