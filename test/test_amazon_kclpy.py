# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from mock import Mock
from amazon_kclpy import kcl, dispatch
from utils import make_io_obj


def build_basic_io_handler_mock(read_line_side_effects):
    """

    :param read_line_side_effects:
    :rtype: kcl._IOHandler
    """
    io_handler = Mock()
    io_handler.read_line.side_effect = read_line_side_effects
    io_handler.load_action.side_effect = lambda x: json.loads(x, object_hook=dispatch.message_decode)
    return io_handler


def test_checkpointer_exception():
    exception_name = 'ThisIsATestException'
    checkpointer = kcl.Checkpointer(
        build_basic_io_handler_mock(['{"action": "checkpoint",'
                                     '"checkpoint":"456", "sequenceNumber": "1234", "subSequenceNumber": 0, '
                                     '"error" : "' + exception_name + '"}']))
    try:
        checkpointer.checkpoint()
        assert 0, "Checkpointing should have raised an exception"
    except kcl.CheckpointError as e:
        assert e.value == exception_name


def test_checkpointer_unexpected_message_after_checkpointing():
    io_handler = Mock()
    io_handler.read_line.side_effect = ['{"action":"initialize", "shardId" : "shardid-123", '
                                        '"sequenceNumber": "1234", "subSequenceNumber": 1}', ]
    io_handler.load_action.side_effect = lambda x: json.loads(x, object_hook=dispatch.message_decode)
    checkpointer = kcl.Checkpointer(
        build_basic_io_handler_mock(
            ['{"action":"initialize", "shardId" : "shardid-123", "sequenceNumber": "1234", "subSequenceNumber": 1}']))

    try:
        checkpointer.checkpoint()
        assert 0, "Checkpointing should have raised an exception"
    except kcl.CheckpointError as e:
        assert e.value == 'InvalidStateException'


def test_kcl_process_exits_on_record_processor_exception():
    unique_string = "Super uniqe statement we can look for"
    errorFile = make_io_obj()
    class ClientException(Exception):
        pass
    mock_rp = Mock()  # type: kcl.RecordProcessorBase
    # Our record processor will just fail during initialization
    mock_rp.initialize.side_effect = [ClientException(unique_string)]
    kcl_process = kcl.KCLProcess(mock_rp,
                             input_file=make_io_obj('{"action":"initialize", "shardId" : "shardid-123", '
                                                   '"sequenceNumber": "1234", "subSequenceNumber": 1}'),
                             output_file=make_io_obj(),
                             error_file=errorFile)
    try:
        kcl_process.run()
    except ClientException:
        assert 0, "Should not have seen the ClientException propagate up the call stack."
    assert errorFile.getvalue().count(unique_string) > 0, 'We should see our error message printed to the error file'


def test_kcl_process_exits_on_action_message_exception():
    mock_rp = Mock()  # type: kcl.RecordProcessorBase
    # Our record processor will just fail during initialization
    kcl_process = kcl.KCLProcess(mock_rp,
                                 # This will suffice because a checkpoint message won't be understood by
                                 # the KCLProcessor (only the Checkpointer understands them)
                             input_file=make_io_obj('{"action":"invalid", "error" : "badstuff", '
                                                   '"sequenceNumber": "1234", "subSequenceNumber": 1}'),
                             output_file=make_io_obj(),
                             error_file=make_io_obj())
    try:
        kcl_process.run()
        assert 0, 'Should have received an exception here'
    except dispatch.MalformedAction:
        pass

