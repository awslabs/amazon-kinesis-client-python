# Copyright 2014-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import abc
import json
import sys
import traceback

from amazon_kclpy import dispatch
from amazon_kclpy.v2 import processor as v2processor
from amazon_kclpy.v3 import processor as v3processor
from amazon_kclpy import messages
from amazon_kclpy.checkpoint_error import CheckpointError


class _IOHandler(object):
    """
    Hidden class used by :class:`KCLProcess` and :class:`Checkpointer` to communicate with the input and output
    files.
    """

    def __init__(self, input_file, output_file, error_file):
        """
        :param file input_file: A file to read input lines from (e.g. sys.stdin).
        :param file output_file: A file to write output lines to (e.g. sys.stdout).
        :param file error_file: A file to write error lines to (e.g. sys.stderr).
        """
        self.input_file = input_file
        self.output_file = output_file
        self.error_file = error_file

    def write_line(self, line):
        """
        Writes a line to the output file. The line is preceeded and followed by a new line because other libraries
        could be writing to the output file as well (e.g. some libs might write debugging info to STDOUT) so we would
        like to prevent our lines from being interlaced with other messages so the MultiLangDaemon can understand them.

        :param str line: A line to write (e.g. '{"action" : "status", "responseFor" : "<someAction>"}')
        """
        self.output_file.write('\n{line}\n'.format(line=line))
        self.output_file.flush()

    def write_error(self, error_message):
        """
        Write a line to the error file.

        :param str error_message: An error message.
        """
        self.error_file.write('{error_message}\n'.format(error_message=error_message))
        self.error_file.flush()

    def read_line(self):
        """
        Reads a line from the input file.

        :rtype: str
        :return: A single line read from the input_file (e.g. '{"action" : "initialize", "shardId" : "shardId-000001"}')
        """
        return self.input_file.readline()

    def load_action(self, line):
        """
        Decodes a message from the MultiLangDaemon.
        :type line: str
        :param line: A message line that was delivered received from the MultiLangDaemon (e.g.
            '{"action" : "initialize", "shardId" : "shardId-000001"}')

        :rtype: amazon_kclpy.messages.MessageDispatcher
        :return: A callabe action class that contains the action presented in the line
        """
        return json.loads(line, object_hook=dispatch.message_decode)

    def write_action(self, response):
        """
        :type response: dict
        :param response: A dictionary with an action message such as 'checkpoint' or 'status'. For example if the action that was
            just handled by this processor was an 'initialize' action, this dictionary would look like
            {'action' : status', 'responseFor' : 'initialize'}
        """
        self.write_line(json.dumps(response))


CheckpointError = CheckpointError


class Checkpointer(object):
    """
    A checkpointer class which allows you to make checkpoint requests. A checkpoint marks a point in a shard
    where you've successfully processed to. If this processor fails or loses its lease to that shard, another
    processor will be started either by this MultiLangDaemon or a different instance and resume at the most recent
    checkpoint in this shard.
    """
    def __init__(self, io_handler):
        """
        :type io_handler: amazon_kclpy.kcl._IOHandler
        :param io_handler: An IOHandler object which this checkpointer will use to write and read checkpoint actions
            to and from the MultiLangDaemon.
        """
        self.io_handler = io_handler

    def _get_action(self):
        """
        Gets the next json message from STDIN

        :rtype: object
        :return: Either a child of MessageDispatcher, or a housekeeping object type
        """
        line = self.io_handler.read_line()
        action = self.io_handler.load_action(line)
        return action

    def checkpoint(self, sequence_number=None, sub_sequence_number=None):
        """
        Checkpoints at a particular sequence number you provide or if no sequence number is given, the checkpoint will
        be at the end of the most recently delivered list of records

        :param str or None sequence_number: The sequence number to checkpoint at or None if you want to checkpoint at the
            farthest record
        :param int or None sub_sequence_number: the sub sequence to checkpoint at, if set to None will checkpoint
            at the farthest sub_sequence_number
        """
        response = {"action": "checkpoint", "sequenceNumber": sequence_number, "subSequenceNumber": sub_sequence_number}
        self.io_handler.write_action(response)
        action = self._get_action()
        if isinstance(action, messages.CheckpointInput):
            if action.error is not None:
                raise CheckpointError(action.error)
        else:
            #
            # We are in an invalid state. We will raise a checkpoint exception
            # to the RecordProcessor indicating that the KCL (or KCLpy) is in
            # an invalid state. See KCL documentation for description of this
            # exception. Note that the documented guidance is that this exception
            # is NOT retryable so the client code should exit.
            #
            raise CheckpointError('InvalidStateException')


# RecordProcessor base class
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
    def initialize(self, shard_id):
        """
        Called once by a KCLProcess before any calls to process_records

        :type shard_id: str
        :param shard_id: The shard id that this processor is going to be working on.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process_records(self, records, checkpointer):
        """
        Called by a KCLProcess with a list of records to be processed and a checkpointer which accepts sequence numbers
        from the records to indicate where in the stream to checkpoint.

        :type records: list
        :param records: A list of records that are to be processed. A record looks like
            {"data":"<base64 encoded string>","partitionKey":"someKey","sequenceNumber":"1234567890"} Note that "data" is a base64
            encoded string. You can use base64.b64decode to decode the data into a string. We currently do not do this decoding for you
            so as to leave it to your discretion whether you need to decode this particular piece of data.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown(self, checkpointer, reason):
        """
        Called by a KCLProcess instance to indicate that this record processor should shutdown. After this is called,
        there will be no more calls to any other methods of this record processor.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.

        :type reason: str
        :param reason: The reason this record processor is being shutdown, either TERMINATE or ZOMBIE. If ZOMBIE,
            clients should not checkpoint because there is possibly another record processor which has acquired the lease
            for this shard. If TERMINATE then checkpointer.checkpoint() should be called to checkpoint at the end of the
            shard so that this processor will be shutdown and new processor(s) will be created to for the child(ren) of
            this shard.
        """
        raise NotImplementedError

    def shutdown_requested(self, checkpointer):
        """
        Called by a KCLProcess instance to indicate that this record processor is about to be be shutdown.  This gives
        the record processor a chance to checkpoint, before the lease is terminated.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.
        """
        pass

    version = 1


class KCLProcess(object):

    def __init__(self, record_processor, input_file=sys.stdin, output_file=sys.stdout, error_file=sys.stderr):
        """
        :type record_processor: RecordProcessorBase or amazon_kclpy.v2.processor.RecordProcessorBase
        :param record_processor: A record processor to use for processing a shard.

        :param file input_file: A file to read action messages from. Typically STDIN.

        :param file output_file: A file to write action messages to. Typically STDOUT.

        :param file error_file: A file to write error messages to. Typically STDERR.
        """
        self.io_handler = _IOHandler(input_file, output_file, error_file)
        self.checkpointer = Checkpointer(self.io_handler)
        if record_processor.version == 2:
            self.processor = v3processor.V2toV3Processor(record_processor)
        elif record_processor.version == 1:
            self.processor = v3processor.V2toV3Processor(v2processor.V1toV2Processor(record_processor))
        else:
            self.processor = record_processor

    def _perform_action(self, action):
        """
        Maps input action to the appropriate method of the record processor.

        :type action:
        :param MessageDispatcher action: A derivative of MessageDispatcher that will handle the provided input

        :raises MalformedAction: Raised if the action is missing attributes.
        """

        try:
            action.dispatch(self.checkpointer, self.processor)
        except SystemExit as sys_exit:
            # On a system exit exception just go ahead and exit
            raise sys_exit
        except Exception as ex:
            """
            We don't know what the client's code could raise and we have no way to recover if we let it propagate
            up further. We will mimic the KCL and pass over client errors. We print their stack trace to STDERR to
            help them notice and debug this type of issue.
            """
            self.io_handler.error_file.write("Caught exception from action dispatch: {ex}".format(ex=str(ex)))
            traceback.print_exc(file=self.io_handler.error_file)
            self.io_handler.error_file.flush()

    def _report_done(self, response_for=None):
        """
        Writes a status message to the output file.

        :param response_for: Required parameter; the action that this status message is confirming completed.
        """
        self.io_handler.write_action({"action": "status", "responseFor": response_for})

    def _handle_a_line(self, line):
        """
        - Parses the line from JSON
        - Invokes the appropriate method of the RecordProcessor
        - Writes a status message back to MultiLanguageDaemon

        :type line: str
        :param line: A line that has been read from STDIN and is expected to be a JSON encoded dictionary
            representing what action to take.
        """
        action = self.io_handler.load_action(line)
        self._perform_action(action)
        self._report_done(action.action)

    def run(self):
        """
        Starts this KCL processor's main loop.
        """
        line = True
        """
        We don't make any effort to stop errors from propagating up and exiting the program
        because there is really nothing the KCLpy can do to recover after most exceptions that could
        occur, e.g. I/O error or json decoding exception (the MultiLangDaemon should never write a non-json string
        to this process).
        """
        while line:
            line = self.io_handler.read_line()
            if line:
                self._handle_a_line(line)


