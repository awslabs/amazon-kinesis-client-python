# Copyright 2014-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
# http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
import abc
import base64
from datetime import datetime


class MessageDispatcher(object):
    """
    The base class use to dispatch actions to record processors.  This allows derived classes
    to determine which method on the record processor they need to call.  Additionally classes
    implementing this generally wrap up the parameters into themselves
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def dispatch(self, checkpointer, record_processor):
        """
        Dispatches the current message to the record processor.

        :param amazon_kclpy.kcl.Checkpointer checkpointer: The checkpointer that can be used by the record
            process to record its progress

        :param amazon_kclpy.v2.processor.RecordProcessorBase record_processor: The record processor that will receive,
            and process the message.

        :return: Nothing
        """
        raise NotImplementedError

    @abc.abstractmethod
    def action(self):
        """
        Retrieves the name of the action that caused the creation of this dispatcher.

        :return str: The name of the action e.g. initialize, or processRecords
        """
        raise NotImplementedError


class InitializeInput(MessageDispatcher):
    """
    Provides the necessary parameters to initialize a Record Processor
    """
    def __init__(self, json_dict):
        """
        Configures the input, preparing it for dispatch

        :param dict json_dict: The raw representation of the JSON data
        """
        self._shard_id = json_dict["shardId"]
        self._sequence_number = json_dict["sequenceNumber"]
        self._sub_sequence_number = json_dict["subSequenceNumber"]
        self._action = json_dict['action']

    @property
    def shard_id(self):
        """
        The shard id that this record processor will be processing.

        :return: the shard id
        :rtype: str
        """
        return self._shard_id

    @property
    def sequence_number(self):
        """
        The sequence number that this record processor will start at.  This can be None if this record processor is
        starting on a fresh shard.

        :return: the sequence number
        :rtype: str or None
        """
        return self._sequence_number

    @property
    def sub_sequence_number(self):
        """
        The sub sequence number that this record processor will start at.  This will never be none,
        but can be 0 if there was no sub-sequence number

        :return: the subsequence number
        :rtype: int
        """
        return self._sub_sequence_number

    @property
    def action(self):
        """
        The action that spawned this message

        :return: the original action value
        :rtype: str
        """
        return self._action

    def dispatch(self, checkpointer, record_processor):
        record_processor.initialize(self)


class ProcessRecordsInput(MessageDispatcher):
    """
    Provides the records, and associated metadata for calls to process_records.
    """
    def __init__(self, json_dict):
        self._records = json_dict["records"]
        self._millis_behind_latest = json_dict["millisBehindLatest"]
        self._checkpointer = None
        self._action = json_dict['action']

    @property
    def records(self):
        """
        The records that are part of this request.

        :return: records that are part of this request
        :rtype: list[amazon_kclpy.messages.Record]
        """
        return self._records

    @property
    def millis_behind_latest(self):
        """
        An approximation of how far behind the current time this batch of records is.

        :return: the number of milliseconds
        :rtype: int
        """
        return self._millis_behind_latest

    @property
    def checkpointer(self):
        """
        Provides the checkpointer that will confirm all records upto, and including this batch of records.

        :return: the checkpointer for this request
        :rtype: amazon_kclpy.kcl.Checkpointer
        """
        return self._checkpointer

    @property
    def action(self):
        """
        The action that spawned this message

        :return: the original action value
        :rtype: str
        """
        return self._action

    def dispatch(self, checkpointer, record_processor):
        self._checkpointer = checkpointer
        record_processor.process_records(self)


class ShutdownInput(MessageDispatcher):
    """
    Used to tell the record processor it will be shutdown.
    """
    def __init__(self, json_dict):
        self._reason = json_dict["reason"]
        self._checkpointer = None
        self._action = json_dict['action']

    @property
    def reason(self):
        """
        The reason that this record processor is being shutdown, will be one of

        * TERMINATE
        * ZOMBIE

        :return: the reason for the shutdown
        :rtype: str
        """
        return self._reason

    @property
    def checkpointer(self):
        """
        The checkpointer that can be used to checkpoint this shutdown.

        :return: the checkpointer
        :rtype: amazon_kclpy.kcl.Checkpointer
        """
        return self._checkpointer

    @property
    def action(self):
        """
        The action that spawned this message

        :return: the original action value
        :rtype: str
        """
        return self._action

    def dispatch(self, checkpointer, record_processor):
        self._checkpointer = checkpointer
        record_processor.shutdown(self)


class CheckpointInput(object):
    """
    Used in preparing the response back during the checkpoint process.  This shouldn't be used by record processors.
    """
    def __init__(self, json_dict):
        """
        Creates a new CheckpointInput object with the given sequence number, and sub-sequence number.
        The provided dictionary must contain:
        * sequenceNumber
        * subSequenceNumber

        The provided dictionary can optionally contain:
        * error

        :param dict json_dict:
        """
        self._sequence_number = json_dict["sequenceNumber"]
        self._sub_sequence_number = json_dict["subSequenceNumber"]
        self._error = json_dict.get("error", None)

    @property
    def sequence_number(self):
        """
        The sequence number that record processor intends to checkpoint at.  Can be None if the default 
        checkpoint behavior is desired.

        :return: the sequence number
        :rtype: str or None
        """
        return self._sequence_number

    @property
    def sub_sequence_number(self):
        """
        The sub-sequence number that the record processor intends to checkpoint at.  Can be None if 
        the default checkpoint behavior is desired.

        :return: the sub-sequence number
        :rtype: int or None
        """
        return self._sub_sequence_number

    @property
    def error(self):
        """
        The error message that may have resulted from checkpointing.  This will be None if no error occurred.

        :return: the error message
        :rtype: str or None
        """
        return self._error


class Record(object):
    """
    Represents a single record as returned by Kinesis, or Deaggregated from the Kinesis Producer Library
    """
    def __init__(self, json_dict):
        """
        Creates a new Record object that represent a single record in Kinesis.  Construction for the provided
        dictionary requires that the following fields are present:
            * sequenceNumber
            * subSequenceNumber
            * approximateArrivalTimestamp
            * partitionKey
            * data

        :param dict json_dict:
        """
        self._sequence_number = json_dict["sequenceNumber"]
        self._sub_sequence_number = json_dict["subSequenceNumber"]

        self._timestamp_millis = int(json_dict["approximateArrivalTimestamp"])
        self._approximate_arrival_timestamp = datetime.fromtimestamp(self._timestamp_millis / 1000.0)

        self._partition_key = json_dict["partitionKey"]
        self._data = json_dict["data"]
        self._json_dict = json_dict

    @property
    def binary_data(self):
        """
        The raw binary data automatically decoded from the Base 64 representation provided by

        :py:attr:`data` the original source of the data

        :return: a string representing the raw bytes from
        :rtype: str
        """
        return base64.b64decode(self._data)
    
    @property
    def sequence_number(self):
        """
        The sequence number for this record.  This number maybe the same for other records, if they're
        all part of an aggregated record.  In that case the sub_sequence_number will be greater than 0

        :py:attr:`sub_sequence_number`

        :return: the sequence number
        :rtype: str
        """
        return self._sequence_number
    
    @property
    def sub_sequence_number(self):
        """
        The sub-sequence number of this record.  This is only populated when the record is a deaggregated
        record produced by the `amazon-kinesis-producer-library <https://github.com/awslabs/amazon-kinesis-producer>`

        :return: the sub-sequence number
        :rtype: int
        """
        return self._sub_sequence_number

    @property
    def timestamp_millis(self):
        """
        The timestamp of the approximate arrival time of the record in milliseconds since the Unix epoch

        :return: the timestamp in milliseconds
        :rtype: int
        """
        return self._timestamp_millis

    @property
    def approximate_arrival_timestamp(self):
        """
        The approximate time when this record was accepted, and stored by Kinesis.

        :return: the timestamp
        :rtype: datetime
        """
        return self._approximate_arrival_timestamp

    @property
    def partition_key(self):
        """
        The partition key for this record

        :return: the partition key
        :rtype: str
        """
        return self._partition_key

    @property
    def data(self):
        """
        The Base64 encoded data of this record.

        :return: a string containing the Base64 data
        :rtype: str
        """
        return self._data

    def get(self, field):
        return self._json_dict[field]
    
    def __getitem__(self, field):
        return self.get(field)

