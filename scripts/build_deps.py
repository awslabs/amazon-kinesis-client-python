#!/usr/bin/env python
# Copyright 2014-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Builds the dependency list used by setup.py from the maven dependency tree.  This script must be run in the
amazon-kinesis-client or amazon-kinesis-client-multilang directory, or where the pom.xml for the libraries are present.
"""
import subprocess
from tempfile import mkstemp
from os import close
import re


def format_dependency(line):
    """
    This attempts to extract Maven dependencies and versions from a line of output from mvn dependency:tree

    An example line without specifiers:

    ``[INFO] +- software.amazon.kinesis:amazon-kinesis-client:jar:2.1.2:compile``

    This fields in the line in order are:
    1. Group Id: software.amazon.kinesis
    2. Artifact Id: amazon-kinesis-client
    3. Packaging: jar (not used)
    4. Version: 2.1.2
    5. Dependency type: compile (this will be runtime or compile)

    An example line with specifiers:

    ``[INFO] |  |  +- io.netty:netty-transport-native-epoll:jar:linux-x86_64:4.1.32.Final:compile``

    The fields in order are:
    1. Group Id: io.netty
    2. Artifact Id: netty-transport-native-epoll
    3. Packaging: jar (not used)
    4. Specifier: linux-x86_64 (not used)
    5. Version: 4.1.32.Final
    6. Dependency type: compile (this will be runtime or compile)

    :param str line: the line to extract version information from
    :return: the version information needed to retrieve the jars from Maven Central
    """
    match = re.match(r'^[\\\s+|-]*(?P<dep_line>[^\s]+)', line)
    assert match is not None
    items = match.groupdict()['dep_line'].split(":")
    version_idx = 3
    if len(items) > 5:
        version_idx = 4

    return "('{group_id}', '{artifact_id}', '{version}')".format(group_id=items[0],
                                                                 artifact_id=items[1],
                                                                 version=items[version_idx])


def build_deps():
    """
    Extracts all the dependencies from the pom.xml and formats them into a form usable for setup.py or other
    multilang daemon implementations
    """
    (fh, filename) = mkstemp()
    close(fh)
    output_command = '-Doutput={temp}'.format(temp=filename)
    subprocess.check_call(['mvn', 'dependency:tree', '-Dscope=runtime', output_command])

    dependency_file = open(filename)

    dependencies = [format_dependency(line) for line in dependency_file]

    print(",\n".join(dependencies))


if __name__ == '__main__':
    build_deps()

