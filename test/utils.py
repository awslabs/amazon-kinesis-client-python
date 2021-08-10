# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import sys
import io


def make_io_obj(json_text=None):
    if sys.version_info[0] >= 3:
        create_method = io.StringIO
    else:
        create_method = io.BytesIO

    if json_text is not None:
        return create_method(json_text)
    else:
        return create_method()