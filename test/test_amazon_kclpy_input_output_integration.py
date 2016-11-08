import json
import io
import re

from amazon_kclpy import kcl


# Dummy record processor
class RecordProcessor(kcl.RecordProcessorBase):

    def __init__(self, expected_shard_id, expected_sequence_number):
        self.expected_shard_id = expected_shard_id
        self.expected_sequence_number = expected_sequence_number
        pass

    def initialize(self, shard_id):
        assert shard_id == self.expected_shard_id
        pass

    def process_records(self, records, checkpointer):
        seq = records[0].get('sequenceNumber')
        assert seq == self.expected_sequence_number
        try:
            checkpointer.checkpoint(seq)
            assert 0, "First checkpoint should fail"
        except Exception:
            # Try it one more time (this time it'll work)
            checkpointer.checkpoint(seq)

    def shutdown(self, checkpointer, reason):
        if 'TERMINATE' == reason:
            checkpointer.checkpoint()

'''
An input string which we'll feed to a file for kcl.py to read from.
'''

'''
This string is approximately what the output should look like. We remove whitespace when comparing this to what is
written to the outputfile.
'''
test_output_string = """
{"action": "status", "responseFor": "initialize"}
{"action": "checkpoint", "checkpoint": "456"}
{"action": "checkpoint", "checkpoint": "456"}
{"action": "status", "responseFor": "processRecords"}
{"action": "checkpoint", "checkpoint": null}
{"action": "status", "responseFor": "shutdown"}
"""

test_output_messages = [
    {"action": "status", "responseFor": "initialize"},
    {"action": "checkpoint", "sequenceNumber": "456", "subSequenceNumber": None},
    {"action": "checkpoint", "sequenceNumber": "456", "subSequenceNumber": None},
    {"action": "status", "responseFor": "processRecords"},
    {"action": "checkpoint", "sequenceNumber": None, "subSequenceNumber": None},
    {"action": "status", "responseFor": "shutdown"}
]

def _strip_all_whitespace(s):
    return re.sub('\s*', '', s)

test_shard_id = "shardId-123"
test_sequence_number = "456"

test_input_messages = [
    {"action": "initialize", "shardId": test_shard_id, "sequenceNumber": test_sequence_number, "subSequenceNumber": 0},
    {"action": "processRecords", "millisBehindLatest": 1476889708000, "records":
        [
            {
                "action": "record", "data": "bWVvdw==", "partitionKey": "cat", "sequenceNumber": test_sequence_number,
                "subSequenceNumber": 0, "approximateArrivalTimestamp": 1476889707000
            }
        ]
     },
    {"action": "checkpoint", "sequenceNumber": test_sequence_number, "subSequenceNumber": 0, "error": "Exception"},
    {"action": "checkpoint", "sequenceNumber": test_sequence_number, "subSequenceNumber": 0},
    {"action": "shutdown", "reason": "TERMINATE"},
    {"action": "checkpoint", "sequenceNumber": test_sequence_number, "subSequenceNumber": 0}
]


def test_kcl_py_integration_test_perfect_input():
    test_input_json = "\n".join(map(lambda j: json.dumps(j), test_input_messages))
    input_file = io.BytesIO(test_input_json)
    output_file = io.BytesIO()
    error_file = io.BytesIO()
    process = kcl.KCLProcess(RecordProcessor(test_shard_id, test_sequence_number),
                             input_file=input_file, output_file=output_file, error_file=error_file)
    process.run()
    '''
    The strings are approximately the same, modulo whitespace.
    '''
    output_message_list = filter(lambda s: s != "", output_file.getvalue().split("\n"))
    responses = map(lambda s: json.loads(s), output_message_list)
    assert len(responses) == len(test_output_messages)
    for i in range(len(responses)):
        assert responses[i] == test_output_messages[i]

    '''
    There should be some error output but it seems like overly specific to make sure that a particular message is printed.
    '''
    error_output = error_file.getvalue()
    assert error_output == ""
