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