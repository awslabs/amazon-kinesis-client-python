# Copyright 2014-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import abc


class RecordProcessorBase(object):
    """
    Base class for implementing a record processor.A RecordProcessor processes a shard in a stream.
    Its methods will be called with this pattern:

    - initialize will be called once
    - process_records will be called zero or more times
    - shutdown will be called if this MultiLangDaemon instance loses the lease to this shard
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, initialize_input):
        """
        Called once by a KCLProcess before any calls to process_records

        :param amazon_kclpy.messages.InitializeInput initialize_input: Information about the
            initialization request for the record processor
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process_records(self, process_records_input):
        """
        Called by a KCLProcess with a list of records to be processed and a checkpointer which accepts sequence numbers
        from the records to indicate where in the stream to checkpoint.

        :param amazon_kclpy.messages.ProcessRecordsInput process_records_input: the records, and metadata about the
            records.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown(self, shutdown_input):
        """
        Called by a KCLProcess instance to indicate that this record processor should shutdown. After this is called,
        there will be no more calls to any other methods of this record processor.

        As part of the shutdown process you must inspect :attr:`amazon_kclpy.messages.ShutdownInput.reason` to
        determine the steps to take.

            * Shutdown Reason ZOMBIE:
                **ATTEMPTING TO CHECKPOINT ONCE A LEASE IS LOST WILL FAIL**

                A record processor will be shutdown if it loses its lease.  In this case the KCL will terminate the
                record processor.  It is not possible to checkpoint once a record processor has lost its lease.
            * Shutdown Reason TERMINATE:
                **THE RECORD PROCESSOR MUST CHECKPOINT OR THE KCL WILL BE UNABLE TO PROGRESS**

                A record processor will be shutdown once it reaches the end of a shard.  A shard ending indicates that
                it has been either split into multiple shards or merged with another shard.  To begin processing the new
                shard(s) it's required that a final checkpoint occurs.


        :param amazon_kclpy.messages.ShutdownInput shutdown_input: Information related to the shutdown request
        """
        raise NotImplementedError

    def shutdown_requested(self, shutdown_requested_input):
        """
        Called by a KCLProcess instance to indicate that this record processor is about to be be shutdown.  This gives
        the record processor a chance to checkpoint, before the lease is terminated.

        :param amazon_kclpy.messages.ShutdownRequestedInput shutdown_requested_input:
            Information related to shutdown requested.
        """
        pass

    version = 2


class V1toV2Processor(RecordProcessorBase):
    """
    Provides a bridge between the new v2 RecordProcessorBase, and the original RecordProcessorBase.

    This handles the conversion of the new input types to the older expected forms.  This normally shouldn't be used
    directly by record processors, since it's just a compatibility layer.

    The delegate should be a :py:class:`amazon_kclpy.kcl.RecordProcessorBase`:

    """
    def __init__(self, delegate):
        """
        Creates a new V1 to V2 record processor.

        :param amazon_kclpy.kcl.RecordProcessorBase delegate: the delegate where requests will be forwarded to
        """
        self.delegate = delegate

    def initialize(self, initialize_input):
        """
        Initializes the record processor

        :param amazon_kclpy.messages.InitializeInput initialize_input: the initialization request
        :return: None
        """
        self.delegate.initialize(initialize_input.shard_id)

    def process_records(self, process_records_input):
        """
        Expands the requests, and hands it off to the delegate for processing

        :param amazon_kclpy.messages.ProcessRecordsInput process_records_input: information about the records
            to process
        :return: None
        """
        self.delegate.process_records(process_records_input.records, process_records_input.checkpointer)

    def shutdown(self, shutdown_input):
        """
        Sends the shutdown request to the delegate

        :param amazon_kclpy.messages.ShutdownInput shutdown_input: information related to the record processor shutdown
        :return: None
        """
        self.delegate.shutdown(shutdown_input.checkpointer, shutdown_input.reason)

    def shutdown_requested(self, shutdown_requested_input):
        """
        Sends the shutdown request to the delegate

        :param amazon_kclpy.messages.ShutdownInput shutdown_input: information related to the record processor shutdown
        :return: None
        """
        self.delegate.shutdown_requested(shutdown_requested_input.checkpointer)
