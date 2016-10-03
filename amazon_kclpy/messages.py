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
import abc
import base64
from datetime import datetime
from datetime import timedelta


class MessageDispatcher(object):
    """
    The base class use to dispatch actions to record processors.  This allows derived classes to determine which method on the record processor they 
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def dispatch(self, checkpointer, record_processor):
        pass


class InitializeInput(MessageDispatcher):

    def __init__(self, json_dict):
        self.shard_id = json_dict["shardId"]
        self.sequence_number = json_dict["sequenceNumber"]
        self.sub_sequence_number = json_dict["subSequenceNumber"]
        self.action = get_action(json_dict)

    def dispatch(self, checkpointer, record_processor):
        record_processor.initialize(self)


class ProcessRecordsInput(MessageDispatcher):

    def __init__(self, json_dict):
        self.records = json_dict["records"]
        self.millis_behind_latest = json_dict["millisBehindLatest"]
        self.checkpointer = None
        self.action = get_action(json_dict)

    def dispatch(self, checkpointer, record_processor):
        self.checkpointer = checkpointer
        record_processor.process_records(self)


class ShutdownInput(MessageDispatcher):

    def __init__(self, json_dict):
        self.reason = json_dict["reason"]
        self.checkpointer = None
        self.action = get_action(json_dict)

    def dispatch(self, checkpointer, record_processor):
        self.checkpointer = checkpointer
        record_processor.shutdown(self)


class CheckpointInput(object):

    def __init__(self, json_dict):
        self.sequence_number = json_dict["sequenceNumber"]
        self.sub_sequence_number = json_dict["subSequenceNumber"]
        self.error = json_dict["error"]


class Record(object):

    def __init__(self, json_dict):
        self.sequence_number = json_dict["sequenceNumber"]
        self.sub_sequence_number = json_dict["subSequenceNumber"]

        self.java_time_stamp = int(json_dict["approximateArrivalTimestamp"])
        millis = timedelta(milliseconds=self.java_time_stamp % 1000)
        seconds = self.java_time_stamp / 1000
        self.approximate_arrival_timestamp = datetime.fromtimestamp(seconds) + millis

        self.partition_key = json_dict["partitionKey"]
        self.data = json_dict["data"]
        self.json_dict = json_dict

    @property
    def binary_data(self):
        return base64.b64decode(self.data)

    def get(self, field):
        return self.json_dict[field]


def get_action(dct):
    return dct['action']