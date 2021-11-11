# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

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
    "record": messages.Record,
    "shutdownRequested": messages.ShutdownRequestedInput,
    "leaseLost": messages.LeaseLostInput,
    "shardEnded": messages.ShardEndedInput,
}


def _format_serializer_names():
    return ", ".join('"{k}"'.format(k=k) for k in _serializers.keys())


def message_decode(json_dict):
    """
    Translates incoming JSON commands into MessageDispatch classes

    :param dict json_dict: a dictionary of JSON data

    :return: an object that can be used to dispatch the received JSON command
    :rtype: amazon_kclpy.messages.MessageDispatcher

    :raises MalformedAction: if the JSON object is missing action, or an appropriate serializer for that
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
