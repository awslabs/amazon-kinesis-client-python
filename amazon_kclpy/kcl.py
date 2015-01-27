'''
Copyright 2014-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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

class _IOHandler(object):
    '''
    Hidden class used by :class:`KCLProcess` and :class:`Checkpointer` to communicate with the input and output
    files.
    '''

    def __init__(self, input_file, output_file, error_file):
        '''
        :type input_file: file
        :param input_file: A file to read input lines from (e.g. sys.stdin).

        :type output_file: file
        :param output_file: A file to write output lines to (e.g. sys.stdout).

        :type error_file: file
        :param error_file: A file to write error lines to (e.g. sys.stderr).
        '''
        self.input_file = input_file
        self.output_file = output_file
        self.error_file = error_file

    def write_line(self, line):
        '''
        Writes a line to the output file. The line is preceeded and followed by a new line because other libraries
        could be writing to the output file as well (e.g. some libs might write debugging info to STDOUT) so we would
        like to prevent our lines from being interlaced with other messages so the MultiLangDaemon can understand them.

        :type l: str
        :param l: A line to write (e.g. '{"action" : "status", "responseFor" : "<someAction>"}')
        '''
        self.output_file.write('\n{line}\n'.format(line=line))
        self.output_file.flush()

    def write_error(self, error_message):
        '''
        Write a line to the error file.
        :type error_message: str
        :param error_message: An error message.
        '''
        self.error_file.write('{error_message}\n'.format(error_message=error_message))
        self.error_file.flush()

    def read_line(self):
        '''
        Reads a line from the input file.

        :rtype: str
        :return: A single line read from the input_file (e.g. '{"action" : "initialize", "shardId" : "shardId-000001"}')
        '''
        return self.input_file.readline()

    def load_action(self, line):
        '''
        Decodes a message from the MultiLangDaemon.
        :type line: str
        :param line: A message line that was delivered received from the MultiLangDaemon (e.g.
            '{"action" : "initialize", "shardId" : "shardId-000001"}')

        :rtype: dict
        :return: A dictionary representing the contents of the line (e.g. {"action" : "initialize", "shardId" : "shardId-000001"})
        '''
        return json.loads(line)

    def write_action(self, response):
        '''
        :type response: dict
        :param response: A dictionary with an action message such as 'checkpoint' or 'status'. For example if the action that was
            just handled by this processor was an 'initialize' action, this dictionary would look like
            {'action' : status', 'responseFor' : 'initialize'}
        '''
        self.write_line(json.dumps(response))


class CheckpointError(Exception):
    '''
    Error class used for wrapping exception names passed through the input file.
    '''
    def __init__(self, value):
        '''
        :type value: str
        :param value: The name of the exception that was received while checkpointing. For more details see
            https://github.com/awslabs/amazon-kinesis-client/tree/master/src/main/java/com/amazonaws/services/kinesis/clientlibrary/exceptions
            Any of those exceptions' names could be returned by the MultiLangDaemon as a response to a checkpoint action.
        '''
        self.value = value

    def __str__(self):
        return repr(self.value)

class Checkpointer(object):
    '''
    A checkpointer class which allows you to make checkpoint requests. A checkpoint marks a point in a shard
    where you've successfully processed to. If this processor fails or loses its lease to that shard, another
    processor will be started either by this MultiLangDaemon or a different instance and resume at the most recent
    checkpoint in this shard.
    '''
    def __init__(self, io_handler):
        '''
        :type io_handler: amazon_kclpy.kcl._IOHandler
        :param io_handler: An IOHandler object which this checkpointer will use to write and read checkpoint actions
            to and from the MultiLangDaemon.
        '''
        self.io_handler = io_handler

    def _get_action(self):
        '''
        Gets the next json message from STDIN

        :rtype: dict
        :return: A dictionary object that indicates what action this processor should take next. For example
            {"action" : "initialize", "shardId" : "shardId-000001"} would indicate that this processor should
            invoke the initialize method of the inclosed RecordProcessor object.
        '''
        line = self.io_handler.read_line()
        action = self.io_handler.load_action(line)
        return action

    def checkpoint(self, sequenceNumber=None):
        '''
        Checkpoints at a particular sequence number you provide or if no sequence number is given, the checkpoint will
        be at the end of the most recently delivered list of records

        :type sequenceNumber: str
        :param sequenceNumber: The sequence number to checkpoint at or None if you want to checkpoint at the farthest record
        '''
        response = {"action" : "checkpoint", "checkpoint" : sequenceNumber}
        self.io_handler.write_action(response)
        action = self._get_action()
        if action.get('action') == 'checkpoint':
            if action.get('error') != None:
                raise CheckpointError(action.get('error'))
        else:
            '''
            We are in an invalid state. We will raise a checkpoint exception
            to the RecordProcessor indicating that the KCL (or KCLpy) is in
            an invalid state. See KCL documentation for description of this
            exception. Note that the documented guidance is that this exception
            is NOT retryable so the client code should exit.
            '''
            raise CheckpointError('InvalidStateException')

# RecordProcessor base class
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
    def initialize(self, shard_id):
        '''
        Called once by a KCLProcess before any calls to process_records

        :type shard_id: str
        :param shard_id: The shard id that this processor is going to be working on.
        '''
        return

    @abc.abstractmethod
    def process_records(self, records, checkpointer):
        '''
        Called by a KCLProcess with a list of records to be processed and a checkpointer which accepts sequence numbers
        from the records to indicate where in the stream to checkpoint.

        :type records: list
        :param records: A list of records that are to be processed. A record looks like
            {"data":"<base64 encoded string>","partitionKey":"someKey","sequenceNumber":"1234567890"} Note that "data" is a base64
            encoded string. You can use base64.b64decode to decode the data into a string. We currently do not do this decoding for you
            so as to leave it to your discretion whether you need to decode this particular piece of data.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.
        '''
        return

    @abc.abstractmethod
    def shutdown(self, checkpointer, reason):
        '''
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
        '''
        return

class MalformedAction(Exception):
    '''
    Raised when an action given by the MultiLangDaemon doesn't have all the appropriate attributes.
    '''
    pass

class KCLProcess(object):

    def __init__(self, record_processor, inputfile=sys.stdin, outputfile=sys.stdout, errorfile=sys.stderr):
        '''
        :type record_processor: amazon_kclpy.kcl.RecordProcessorBase
        :param record_processor: A record processor to use for processing a shard.

        :type inputfile: file
        :param inputfile: A file to read action messages from. Typically STDIN.

        :type outputfile: file
        :param outputfile: A file to write action messages to. Typically STDOUT.

        :type errorfile: file
        :param errorfile: A file to write error messages to. Typically STDERR.
        '''
        self.io_handler = _IOHandler(inputfile, outputfile, errorfile)
        self.checkpointer = Checkpointer(self.io_handler)
        self.processor = record_processor

    def _perform_action(self, action):
        '''
        Maps input action to the appropriate method of the record processor.

        :type action: dict
        :param action: A dictionary that represents an action to take with appropriate attributes e.g.
            {"action":"initialize","shardId":"shardId-123"}
            {"action":"processRecords","records":[{"data":"bWVvdw==","partitionKey":"cat","sequenceNumber":"456"}]}
            {"action":"shutdown","reason":"TERMINATE"}

        :raises MalformedAction: Raised if the action is missing attributes.
        '''
        try:
            action_type = action['action']
            if action_type == 'initialize':
                args = (action['shardId'],)
                f = self.processor.initialize
            elif action_type == 'processRecords':
                args = (action['records'], self.checkpointer)
                f = self.processor.process_records
            elif action_type == 'shutdown':
                args = (self.checkpointer, action['reason'])
                f = self.processor.shutdown
            else:
                raise MalformedAction("Received an action which couldn't be understood. Action was '{action}'".format(action=action))
        except KeyError as key_error:
            raise MalformedAction("Action {action} was expected to have key {key}".format(action=action, key=str(key_error)))
        try:
            f(*args)
        except:
            '''
            We don't know what the client's code could raise and we have no way to recover if we let it propagate
            up further. We will mimic the KCL and pass over client errors. We print their stack trace to STDERR to
            help them notice and debug this type of issue.
            '''
            traceback.print_exc(file=self.io_handler.error_file)
            self.io_handler.error_file.flush()

    def _report_done(self, response_for=None):
        '''
        Writes a status message to the output file.

        :param response_for: Required parameter; the action that this status message is confirming completed.
        '''
        self.io_handler.write_action({"action" : "status", "responseFor" : response_for})

    def _handle_a_line(self, line):
        '''
        - Parses the line from JSON
        - Invokes the appropriate method of the RecordProcessor
        - Writes a status message back to MultiLanguageDaemon

        :type line: str
        :param line: A line that has been read from STDIN and is expected to be a JSON encoded dictionary
            representing what action to take.
        '''
        action = self.io_handler.load_action(line)
        self._perform_action(action)
        self._report_done(action.get('action'))


    def run(self):
        '''
        Starts this KCL processor's main loop.
        '''
        line = True
        '''
        We don't make any effort to stop errors from propagating up and exiting the program
        because there is really nothing the KCLpy can do to recover after most exceptions that could
        occur, e.g. I/O error or json decoding exception (the MultiLangDaemon should never write a non-json string
        to this process).
        '''
        while line:
            line = self.io_handler.read_line()
            if line:
                self._handle_a_line(line)


