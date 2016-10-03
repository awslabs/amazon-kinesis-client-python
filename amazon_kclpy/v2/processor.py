'''
Copyright 2014-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
'''
import abc, base64, io, json, os, random, sys, time, traceback


class RecordProcessorBase(object):
    '''
    Base class for implementing a record processor.A RecordProcessor processes a shard in a stream.
    Its methods will be called with this pattern:

    - initialize will be called once
    - process_records will be called zero or more times
    - shutdown will be called if this MultiLangDaemon instance loses the lease to this shard
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, initialize_input):
        '''
        Called once by a KCLProcess before any calls to process_records

        :type initialize_input: amazon_kclpy.messages.InitializeInput
        :param initialize_input: Information about the initialization request for the record processor
        '''
        return

    @abc.abstractmethod
    def process_records(self, process_records_input):
        '''
        Called by a KCLProcess with a list of records to be processed and a checkpointer which accepts sequence numbers
        from the records to indicate where in the stream to checkpoint.

        :type process_records_input:  amazon_kclpy.messages.ProcessRecordsInput
        :param process_records_input:

        '''
        return

    @abc.abstractmethod
    def shutdown(self, shutdown_input):
        '''
        Called by a KCLProcess instance to indicate that this record processor should shutdown. After this is called,
        there will be no more calls to any other methods of this record processor.

        :type shutdown_input: amazon_kclpy.messages.ShutdownInput
        :param shutdown_input: Information related to the shutdown request

        :type reason: str
        :param reason: The reason this record processor is being shutdown, either TERMINATE or ZOMBIE. If ZOMBIE,
            clients should not checkpoint because there is possibly another record processor which has acquired the lease
            for this shard. If TERMINATE then checkpointer.checkpoint() should be called to checkpoint at the end of the
            shard so that this processor will be shutdown and new processor(s) will be created to for the child(ren) of
            this shard.
        '''
        return

    def version(self):
        return 2


class V1toV2Processor(RecordProcessorBase):

    def __init__(self,
                 delegate  # type: amazon_kclpy.kcl.RecordProcessorBase
                 ):
        self.delegate = delegate

    def initialize(self, initialize_input):
        # type: (amazon_kclpy.messages.InitializeInput) -> None
        return self.delegate.initialize(initialize_input.shard_id)

    def process_records(self, process_records_input):
        # type: (amazon_kclpy.messages.ProcessRecordsInput) -> None
        self.delegate.process_records(process_records_input.records, process_records_input.checkpointer)

    def shutdown(self, shutdown_input):
        # type: (amazon_kclpy.messages.ShutdownInput) -> None
        self.delegate.shutdown(shutdown_input.checkpointer, shutdown_input.reason)