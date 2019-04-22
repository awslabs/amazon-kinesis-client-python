# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class CheckpointError(Exception):
    """
    Error class used for wrapping exception names passed through the input file.
    """
    def __init__(self, value):
        """
        :type value: str
        :param value: The name of the exception that was received while checkpointing. For more details see
            https://github.com/awslabs/amazon-kinesis-client/tree/master/src/main/java/com/amazonaws/services/kinesis/clientlibrary/exceptions
            Any of those exceptions' names could be returned by the MultiLangDaemon as a response to a checkpoint action.
        """
        self.value = value

    def __str__(self):
        return repr(self.value)

