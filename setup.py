# Copyright 2014-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from __future__ import print_function

import glob
import sys

import os
import shutil
from setuptools import Command
from setuptools import setup
from setuptools.command.install import install

if sys.version_info[0] >= 3:
    # Python 3
    from urllib.request import urlopen
else:
    # Python 2
    from urllib2 import urlopen

#
# This script modifies the basic setuptools by adding some functionality to the standard
# "install" command and by adding an additional command "download_jars" which
# simplifies retrieval of the jars required to run the KCL multi-language daemon
# which is required to run the sample app included in this package.
#
# If a user runs the basic install:
#
#     python setup.py install
#
# They will be notified of any jars that are downloaded for this package. Those jars
# will go in amazon_kclpy/jars so that they can be installed as part of this package's
# data.
#
#     python setup.py download_jars
#
# Will retrieve the configured jars from maven and then advise the user
# to rerun the install command.
#

PACKAGE_NAME = 'amazon_kclpy'
JAR_DIRECTORY = os.path.join(PACKAGE_NAME, 'jars')
PACKAGE_VERSION = '2.0.6'
PYTHON_REQUIREMENTS = [
    'boto',
    # argparse is part of python2.7 but must be declared for python2.6
    'argparse',
]
REMOTE_MAVEN_PACKAGES = [
    # (group id, artifact id, version),
    ('software.amazon.awssdk', 'kinesis', '2.17.52'),
    ('software.amazon.awssdk', 'annotations', '2.17.52'),
    ('software.amazon.awssdk', 'apache-client', '2.17.52'),
    ('software.amazon.awssdk', 'auth', '2.17.52'),
    ('software.amazon.awssdk', 'aws-cbor-protocol', '2.17.52'),
    ('software.amazon.awssdk', 'aws-core', '2.17.52'),
    ('software.amazon.awssdk', 'aws-json-protocol', '2.17.52'),
    ('software.amazon.awssdk', 'aws-query-protocol', '2.17.52'),
    ('software.amazon.awssdk', 'cloudwatch', '2.17.52'),
    ('software.amazon.awssdk', 'dynamodb', '2.17.52'),
    ('software.amazon.awssdk', 'http-client-spi', '2.17.52'),
    ('software.amazon.awssdk', 'json-utils', '2.17.52'),
    ('software.amazon.awssdk', 'metrics-spi', '2.17.52'),
    ('software.amazon.awssdk', 'netty-nio-client', '2.17.52'),
    ('software.amazon.awssdk', 'protocol-core', '2.17.52'),
    ('software.amazon.awssdk', 'profiles', '2.17.52'),
    ('software.amazon.awssdk', 'regions', '2.17.52'),
    ('software.amazon.awssdk', 'sdk-core', '2.17.52'),
    ('software.amazon.awssdk', 'sts', '2.17.52'),
    ('software.amazon.awssdk', 'third-party-jackson-core', '2.17.52'),
    ('software.amazon.awssdk', 'third-party-jackson-dataformat-cbor', '2.17.52'),
    ('software.amazon.awssdk', 'utils', '2.17.52'),
    ('software.amazon.eventstream', 'eventstream', '1.0.1'),
    ('software.amazon.ion', 'ion-java', '1.5.1'),
    ('software.amazon.glue', 'schema-registry-serde', '1.1.5'),
    ('software.amazon.kinesis', 'amazon-kinesis-client-multilang', '2.3.9'),
    ('software.amazon.kinesis', 'amazon-kinesis-client', '2.3.9'),
    ('com.amazonaws', 'aws-java-sdk-core', '1.12.3'),
    ('com.amazonaws', 'aws-java-sdk-sts', '1.12.3'),
    ('com.amazonaws', 'jmespath-java', '1.12.3'),
    ('com.fasterxml.jackson.core', 'jackson-annotations', '2.12.4'),
    ('com.fasterxml.jackson.core', 'jackson-core', '2.12.4'),
    ('com.fasterxml.jackson.core', 'jackson-databind', '2.12.4'),
    ('com.fasterxml.jackson.dataformat', 'jackson-dataformat-cbor', '2.12.4'),
    ('io.netty', 'netty-codec-http', '4.1.68.Final'),
    ('io.netty', 'netty-codec-http2', '4.1.68.Final'),
    ('io.netty', 'netty-codec', '4.1.68.Final'),
    ('io.netty', 'netty-transport', '4.1.68.Final'),
    ('io.netty', 'netty-resolver', '4.1.68.Final'),
    ('io.netty', 'netty-common', '4.1.68.Final'),
    ('io.netty', 'netty-buffer', '4.1.68.Final'),
    ('io.netty', 'netty-handler', '4.1.68.Final'),
    ('io.netty', 'netty-transport-native-epoll', '4.1.68.Final'),
    ('io.netty', 'netty-transport-native-unix-common', '4.1.68.Final'),
    ('io.reactivex.rxjava2', 'rxjava', '2.2.21'),
    ('com.beust', 'jcommander', '1.81'),
    ('com.google.guava', 'guava', '31.0.1-jre'),
    ('com.google.code.findbugs', 'jsr305', '3.0.2'),
    ('com.google.errorprone', 'error_prone_annotations', '2.7.1'),
    ('com.google.j2objc', 'j2objc-annotations', '1.3'),
    ('com.google.protobuf', 'protobuf-java', '3.17.1'),
    ('com.typesafe.netty', 'netty-reactive-streams-http', '2.0.5'),
    ('com.typesafe.netty', 'netty-reactive-streams', '2.0.5'),
    ('org.apache.commons', 'commons-lang3', '3.12.0'),
    ('org.apache.commons', 'commons-collections4', '4.4'),
    ('org.apache.httpcomponents', 'httpclient', '4.5.13'),
    ('org.apache.httpcomponents', 'httpcore', '4.4.14'),
    ('org.checkerframework', 'checker-qual', '2.5.2'),
    ('org.codehaus.mojo', 'animal-sniffer-annotations', '1.20'),
    ('org.reactivestreams', 'reactive-streams', '1.0.3'),
    ('org.slf4j', 'slf4j-api', '1.7.30'),
    ('commons-beanutils', 'commons-beanutils', '1.9.4'),
    ('commons-codec', 'commons-codec', '1.15'),
    ('commons-collections', 'commons-collections', '3.2.2'),
    ('commons-io', 'commons-io', '2.9.0'),
    ('commons-logging', 'commons-logging', '1.2'),
    ('ch.qos.logback', 'logback-classic', '1.2.7'),
    ('ch.qos.logback', 'logback-core', '1.2.7'),
    ('joda-time', 'joda-time', '2.10.10')
]


class MavenJarDownloader:

    def __init__(self, on_completion, destdir=JAR_DIRECTORY, packages=REMOTE_MAVEN_PACKAGES):
        self.on_completion = on_completion
        self.destdir = destdir
        self.packages = packages

    def warning_string(self, missing_jars=[]):
        s = '''The following jars were not installed because they were not
present in this package at the time of installation:'''
        for jar in missing_jars:
            s += '\n  {jar}'.format(jar=jar)
        s += '''
This doesn't affect the rest of the installation, but may make it more
difficult for you to run the sample app and get started.

You should consider running:

    python setup.py download_jars
    python setup.py install

Which will download the required jars and rerun the install.
'''
        return s

    def download_and_check(self):
        self.download_files()
        self.on_completion()
        missing_jars = self.missing_jars()
        if len(missing_jars) > 0:
            raise RuntimeError(self.warning_string(missing_jars))

    def package_destination(self, artifcat_id, version):
        return '{artifcat_id}-{version}.jar'.format(artifcat_id=artifcat_id, version=version)

    def missing_jars(self):
        file_list = [os.path.join(self.destdir, self.package_destination(p[1], p[2])) for p in self.packages]
        return [f for f in file_list if not os.path.isfile(f)] # The missing files

    def package_url(self, group_id, artifact_id, version):
        #
        # Sample url:
        # https://search.maven.org/remotecontent?filepath=org/apache/httpcomponents/httpclient/4.2/httpclient-4.2.jar
        #
        prefix = 'https://search.maven.org/remotecontent?filepath='
        return '{prefix}{path}/{artifact_id}/{version}/{dest}'.format(
                                        prefix=prefix,
                                        path='/'.join(group_id.split('.')),
                                        artifact_id=artifact_id,
                                        version=version,
                                        dest=self.package_destination(artifact_id, version))

    def download_file(self, url, dest):
        """
        Downloads a file at the url to the destination.
        """
        print('Attempting to retrieve remote jar {url}'.format(url=url))
        try:
            response = urlopen(url)
            with open(dest, 'wb') as dest_file:
                shutil.copyfileobj(response, dest_file)
            print('Saving {url} -> {dest}'.format(url=url, dest=dest))
        except Exception as e:
            print('Failed to retrieve {url}: {e}'.format(url=url, e=e))
            return

    def download_files(self):
        for package in self.packages:
            dest = os.path.join(self.destdir, self.package_destination(package[1], package[2]))
            if os.path.isfile(dest):
                print('Skipping download of {dest}'.format(dest=dest))
            else:
                url = self.package_url(package[0], package[1], package[2])
                self.download_file(url, dest)


class DownloadJarsCommand(Command):
    description = "Download the jar files needed to run the sample application"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """
        Runs when this command is given to setup.py
        """
        downloader = MavenJarDownloader(on_completion=lambda : None)
        downloader.download_files()
        print('''
Now you should run:

    python setup.py install

Which will finish the installation.
''')


class InstallThenCheckForJars(install):

    def do_install(self):
        install.run(self)

    def run(self):
        """
        We override the basic install command. First we download jars then
        we run the basic install then we check whether the jars are present
        in this package. If they aren't present we warn the user and give
        them some advice on how to retry getting the jars.
        """
        downloader = MavenJarDownloader(self.do_install)
        downloader.download_and_check()


try:
    from wheel.bdist_wheel import bdist_wheel


    class BdistWheelWithJars(bdist_wheel):
        """
        This overrides the bdist_wheel command, that handles building a binary wheel of the package.
        Currently, as far as I can tell, binary wheel creation only occurs during the virtual environment creation.
        The package that bdist_wheel comes from isn't a modeled dependency of this package, but is required for virtual
        environment creation.
        """

        def do_run(self):
            bdist_wheel.run(self)

        def run(self):
            downloader = MavenJarDownloader(self.do_run)
            downloader.download_and_check()

except ImportError:
    pass

if __name__ == '__main__':
    commands = {
        'download_jars': DownloadJarsCommand,
        'install': InstallThenCheckForJars,
    }
    try:
        #
        # BdistWheelWithJars will only be present if the wheel package is present, and that is present during
        # virtual environment creation.
        # It's important to note this is a hack.  There doesn't appear to be a way to execute hooks around wheel
        # creation by design.  See https://github.com/pypa/packaging-problems/issues/64 for more information.
        #
        commands['bdist_wheel'] = BdistWheelWithJars
    except NameError:
        pass

    setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description='A python interface for the Amazon Kinesis Client Library MultiLangDaemon',
        license='Apache-2.0',
        packages=[PACKAGE_NAME, PACKAGE_NAME + "/v2", PACKAGE_NAME + "/v3", 'samples'],
        scripts=glob.glob('samples/*py'),
        package_data={
            '': ['*.txt', '*.md'],
            PACKAGE_NAME: ['jars/*'],
            'samples': ['sample.properties'],
        },
        install_requires=PYTHON_REQUIREMENTS,
        setup_requires=["pytest-runner"],
        tests_require=["pytest", "mock"],
        cmdclass=commands,
        url="https://github.com/awslabs/amazon-kinesis-client-python",
        keywords="amazon kinesis client library python",
        zip_safe=False,
        )
