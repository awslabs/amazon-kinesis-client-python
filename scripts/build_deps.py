#!/usr/bin/env python
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
"""
Builds the dependency list used by setup.py from the maven dependency tree.  This script must be run in the
amazon-kinesis-client directory, or where the pom.xml for the amazon-kinesis-client is available.
"""
import subprocess
from tempfile import mkstemp
from os import close
import re


def format_dependency(line):
    match = re.match(r'^[\\\s+|-]*(?P<group_id>[^:]+):(?P<artifact_id>[^:]+):[^:]+:(?P<version>[^:\s]+)', line)
    assert match is not None
    return "('{group_id}', '{artifact_id}', '{version}')".format(group_id=match.groupdict()['group_id'],
                                                                 artifact_id=match.groupdict()['artifact_id'],
                                                                 version=match.groupdict()['version'])


def build_deps():
    (fh, filename) = mkstemp()
    close(fh)
    output_command = '-Doutput={temp}'.format(temp=filename)
    subprocess.check_call(['mvn', 'dependency:tree', '-Dscope=runtime', output_command])

    dependency_file = open(filename)

    dependencies = [format_dependency(line) for line in dependency_file]

    print(",\n".join(dependencies))


if __name__ == '__main__':
    build_deps()

