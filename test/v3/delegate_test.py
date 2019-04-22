# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import mock
import pytest

from amazon_kclpy.v2 import processor as v2
from amazon_kclpy.v3 import processor as v3
from amazon_kclpy import messages
from amazon_kclpy.kcl import Checkpointer, CheckpointError


@pytest.fixture
def delegate():
    return mock.Mock(spec=v2.RecordProcessorBase)


@pytest.fixture
def processor(delegate):
    return v3.V2toV3Processor(delegate)


def test_initialization_delegate(delegate, processor):
    initialization_input = mock.Mock(spec=messages.InitializeInput)
    processor.initialize(initialization_input)

    delegate.initialize.assert_called_with(initialization_input)


def test_process_records_delegate(delegate, processor):
    process_records_input = mock.Mock(spec=messages.ProcessRecordsInput)
    processor.process_records(process_records_input)

    delegate.process_records.assert_called_with(process_records_input)


def test_shutdown_requested_delegate(delegate, processor):
    shutdown_requested_input = mock.Mock(spec=messages.ShutdownRequestedInput)
    processor.shutdown_requested(shutdown_requested_input)

    delegate.shutdown_requested.assert_called_with(shutdown_requested_input)


def test_lease_lost_to_shutdown_delegate(delegate, processor):
    lease_lost_input = messages.LeaseLostInput({
        "action": "leaseLost"
    })

    processor.lease_lost(lease_lost_input)
    delegate.shutdown.assert_called()

    actual = delegate.shutdown.call_args[0][0]

    assert actual.reason == "ZOMBIE"
    assert actual.action == "shutdown"
    assert isinstance(actual.checkpointer, messages.LeaseLostCheckpointer)


def test_lease_lost_checkpoint_triggers_exception(delegate, processor):
    lease_lost_input = mock.Mock(spec=messages.LeaseLostInput)
    delegate.shutdown = lambda s: s.checkpointer.checkpoint()

    with pytest.raises(CheckpointError):
        processor.lease_lost(lease_lost_input)


def test_shard_ended_to_shutdown_delegate(delegate, processor):
    shard_ended_input = messages.ShardEndedInput({
        "action": "shardEnded"
    })
    checkpointer = mock.Mock(spec=Checkpointer)
    shard_ended_input._checkpointer = checkpointer

    processor.shard_ended(shard_ended_input)
    delegate.shutdown.assert_called()

    actual = delegate.shutdown.call_args[0][0]

    assert actual.reason == "TERMINATE"
    assert actual.action == "shutdown"
    assert actual.checkpointer == checkpointer

