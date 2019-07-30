# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import abc

from amazon_kclpy.messages import ShutdownInput


class RecordProcessorBase(object):
    """
    Base class for implementing a record processor. Each RecordProcessor processes a single shard in a stream.

    The record processor represents a lifecycle where it will be initialized, possibly process records, and
    finally be terminated.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, initialize_input):
        """
        Called once by a the KCL to allow the record processor to configure itself before starting to process records.

        :param amazon_kclpy.messages.InitializeInput initialize_input: Information about the
            initialization request for the record processor
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process_records(self, process_records_input):
        """
        This is called whenever records are received.  The method will be provided the batch of records that were
        received.  A checkpointer is also supplied that allows the application to checkpoint its progress within the
        shard.

        :param amazon_kclpy.messages.ProcessRecordsInput process_records_input: the records, metadata about the
            records, and a checkpointer.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def lease_lost(self, lease_lost_input):
        """
        This is called whenever the record processor has lost the lease.  After this returns the record processor will
        be shutdown.  Additionally once a lease has been lost checkpointing is no longer possible.

        :param amazon_kclpy.messages.LeaseLostInput lease_lost_input: information about the lease loss (currently empty)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def shard_ended(self, shard_ended_input):
        """
        This is called whenever the record processor has reached the end of the shard. The record processor needs to
        checkpoint to notify the KCL that it's ok to start processing the child shard(s).  Failing to checkpoint will
        trigger a retry of the shard end

        :param amazon_kclpy.messages.ShardEndedInput shard_ended_input: information about reaching the end of the shard.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown_requested(self, shutdown_requested_input):
        """
        Called when the parent process is preparing to shutdown.  This gives the record processor one more chance to
        checkpoint before its lease will be released.

        :param amazon_kclpy.messages.ShutdownRequestedInput shutdown_requested_input:
            Information related to shutdown requested including the checkpointer.
        """
        raise NotImplementedError

    version = 3


class V2toV3Processor(RecordProcessorBase):
    """
    Provides a bridge between the new v2 RecordProcessorBase, and the original RecordProcessorBase.

    This handles the conversion of the new input types to the older expected forms.  This normally shouldn't be used
    directly by record processors, since it's just a compatibility layer.

    The delegate should be a :py:class:`amazon_kclpy.kcl.RecordProcessorBase`:

    """

    def __init__(self, delegate):
        """
        Creates a new V2 to V3 record processor.

        :param amazon_kclpy.kcl.v2.RecordProcessorBase delegate: the delegate where requests will be forwarded to
        """
        self.delegate = delegate

    def initialize(self, initialize_input):
        """
        Initializes the record processor

        :param amazon_kclpy.messages.InitializeInput initialize_input: the initialization request
        :return: None
        """
        self.delegate.initialize(initialize_input)

    def process_records(self, process_records_input):
        """
        Expands the requests, and hands it off to the delegate for processing

        :param amazon_kclpy.messages.ProcessRecordsInput process_records_input: information about the records
            to process
        :return: None
        """
        self.delegate.process_records(process_records_input)

    def lease_lost(self, lease_lost_input):
        """
        Translates the lease lost call to the older shutdown/shutdown input style that was used.  In a special case the
        checkpointer will not be set in this call, which is essentially fine as checkpointing would fail anyway

        :param amazon_kclpy.messages.LeaseLostInput lease_lost_input: information about the lease loss
        (currently this is empty)
        :return: None
        """
        self.delegate.shutdown(ShutdownInput.zombie())

    def shard_ended(self, shard_ended_input):
        """
        Translates the shard end message to a shutdown input with a reason of TERMINATE and the checkpointer
        :param amazon_kclpy.messages.ShardEndedInput shard_ended_input: information, and checkpoint for the end of the
        shard.
        :return: None
        """
        self.delegate.shutdown(ShutdownInput.terminate(shard_ended_input.checkpointer))

    def shutdown_requested(self, shutdown_requested_input):
        """
        Sends the shutdown request to the delegate

        :param amazon_kclpy.messages.ShutdownRequested shutdown_requested_input: information related to the record processor shutdown
        :return: None
        """
        self.delegate.shutdown_requested(shutdown_requested_input)
