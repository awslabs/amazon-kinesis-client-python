import sys
import io
from amazon_kclpy import messages


class MalformedAction(Exception):
    '''
    Raised when an action given by the MultiLangDaemon doesn't have all the appropriate attributes.
    '''
    pass


serializers = {
    "initialize": lambda (json_dict): messages.InitializeInput(json_dict),
    "processRecords": lambda (json_dict): messages.ProcessRecordsInput(json_dict),
    "shutdown": lambda (json_dict): messages.ShutdownInput(json_dict),
    "checkpoint": lambda (json_dict): messages.CheckpointInput(json_dict),
    "record": lambda (json_dict): messages.Record(json_dict)
}


def format_serializer_names():
    return ", ".join(map(lambda k: '"{k}"'.format(k=k), serializers.keys()))


def message_decode(json_dict):

    try:
        action = json_dict["action"]
    except KeyError as key_error:
        raise MalformedAction("Action {json_dict} was expected to have key {key}".format(json_dict=json_dict,
                                                                                         key=str(key_error)))
    try:
        serializer = serializers[action]
    except KeyError:
        raise MalformedAction("Received an action which couldn't be understood. Action was '{action}' -- Allowed {keys}"
                              .format(action=action, keys=format_serializer_names()))

    return serializer(json_dict)