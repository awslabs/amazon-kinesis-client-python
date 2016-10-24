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
from amazon_kclpy import messages


class MalformedAction(Exception):
    """
    Raised when an action given by the MultiLangDaemon doesn't have all the appropriate attributes.
    """
    pass


_serializers = {
    "initialize": messages.InitializeInput,
    "processRecords": messages.ProcessRecordsInput,
    "shutdown": messages.ShutdownInput,
    "checkpoint": messages.CheckpointInput,
    "record": messages.Record
}


def _format_serializer_names():
    return ", ".join('"{k}"'.format(k) for k in _serializers.keys())


def message_decode(json_dict):
    """
    Translates incoming JSON commands into MessageDispatch classes

    :param dict json_dict: a dictionary of JSON data

    :return: an object that can be used to dispatch the received JSON command
    :rtype: amazon_kclpy.messages.MessageDispatcher

    :raises MalformedAction: if the JSON object is missing action, or an appropiate serializer for that
        action can't be found
    """
    try:
        action = json_dict["action"]
    except KeyError as key_error:
        raise MalformedAction("Action {json_dict} was expected to have key {key!s}".format(json_dict=json_dict,
                                                                                           key=key_error))
    try:
        serializer = _serializers[action]
    except KeyError:
        raise MalformedAction("Received an action which couldn't be understood. Action was '{action}' -- Allowed {keys}"
                              .format(action=action, keys=_format_serializer_names()))

    return serializer(json_dict)