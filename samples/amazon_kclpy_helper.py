#!env python
'''
Copyright 2014-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
'''
from __future__ import print_function
from amazon_kclpy import kcl
from glob import glob
import os, argparse, sys, samples

def get_dir_of_file(f):
    '''
    Returns the absolute path to the directory containing the specified file.

    :type f: str
    :param f: A path to a file, either absolute or relative

    :rtype:  str
    :return: The absolute path of the directory represented by the relative path provided.
    '''
    return os.path.dirname(os.path.abspath(f))

def get_kcl_dir():
    '''
    Returns the absolute path to the dir containing the amazon_kclpy.kcl module.

    :rtype: str
    :return: The absolute path of the KCL package. 
    '''
    return get_dir_of_file(kcl.__file__)

def get_kcl_jar_path():
    '''
    Returns the absolute path to the KCL jars needed to run an Amazon KCLpy app.

    :rtype: str
    :return: The absolute path of the KCL jar files needed to run the MultiLangDaemon.
    '''
    return ':'.join(glob(os.path.join(get_kcl_dir(), 'jars', '*jar')))

def get_kcl_classpath(properties=None, paths=[]):
    '''
    Generates a classpath that includes the location of the kcl jars, the
    properties file and the optional paths.

    :type properties: str
    :param properties: Path to properties file.

    :type paths: list
    :param paths: List of strings. The paths that will be prepended to the classpath.

    :rtype: str
    :return: A java class path that will allow your properties to be found and the MultiLangDaemon and its deps and
        any custom paths you provided.
    '''
    # First make all the user provided paths absolute
    paths = [os.path.abspath(p) for p in paths]
    # We add our paths after the user provided paths because this permits users to
    # potentially inject stuff before our paths (otherwise our stuff would always
    # take precedence).
    paths.append(get_kcl_jar_path())
    if properties:
        # Add the dir that the props file is in
        dir_of_file = get_dir_of_file(properties)
        paths.append(dir_of_file)
    return ":".join([p for p in paths if p != ''])

def get_kcl_app_command(java, multi_lang_daemon_class, properties, paths=[]):
    '''
    Generates a command to run the MultiLangDaemon.

    :type java: str
    :param java: Path to java

    :type multi_lang_daemon_class: str
    :param multi_lang_daemon_class: Name of multi language daemon class e.g. com.amazonaws.services.kinesis.multilang.MultiLangDaemon

    :type properties: str
    :param properties: Optional properties file to be included in the classpath.

    :type paths: list
    :param paths: List of strings. Additional paths to prepend to the classpath.

    :rtype: str
    :return: A command that will run the MultiLangDaemon with your properties and custom paths and java.
    '''
    return "{java} -cp {cp} {daemon} {props}".format(java=java,
                                    cp = get_kcl_classpath(properties, paths),
                                    daemon = multi_lang_daemon_class,
                                    # Just need the basename becasue the path is added to the classpath
                                    props = os.path.basename(properties))
'''
This script provides two utility functions:

    --print_classpath - which prints a java class path. It optionally takes --properties
    and any number of --path options. It will generate a java class path which will include
    the properties file and paths and the location of the KCL jars based on the location of
    the amazon_kclpy.kcl module.

    --print_command - which prints a command to run an Amazon KCLpy application. It requires a --java
    and --properties argument and optionally takes any number of --path arguments to prepend
    to the classpath that it generates for the command.
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser("A script for generating a command to run an Amazon KCLpy app")
    parser.add_argument("--print_classpath", dest="print_classpath", action="store_true",
                        default = False,
                        help="Print a java class path.\noptional arguments: --path")
    parser.add_argument("--print_command", dest="print_command", action="store_true",
                        default = False,
                        help="Print a command for running an Amazon KCLpy app.\nrequired "
                        + "args: --java --properties\noptional args: --classpath")
    parser.add_argument("-j", "--java", dest="java",
                        help="The path to the java executable e.g. <some root>/jdk/bin/java",
                        metavar="PATH_TO_JAVA")
    parser.add_argument("-p", "--properties", "--props", "--prop", dest="properties",
                        help="The path to a properties file (relative to where you are running this script)",
                        metavar="PATH_TO_PROPERTIES")
    parser.add_argument("--sample", "--sample-props", "--use-sample-properties", dest="use_sample_props",
                        help="This will use the sample.properties file included in this package as the properties file.",
                        action="store_true", default=False)
    parser.add_argument("-c", "--classpath", "--path", dest="paths", action="append", default=[],
                        help="Additional path to add to java class path. May be specified any number of times",
                        metavar="PATH")
    args = parser.parse_args()
    # Possibly replace the properties with the sample. Useful if they just want to run the sample app.
    if args.use_sample_props:
        if args.properties:
            sys.stderr.write('Replacing provided properties with sample properties due to arg --sample\n')
        args.properties = os.path.join(get_dir_of_file(samples.__file__), 'sample.properties')

    # Print what the asked for
    if args.print_classpath:
        print(get_kcl_classpath(args.properties, args.paths))
    elif args.print_command:
        if args.java and args.properties:
            multi_lang_daemon_class = 'com.amazonaws.services.kinesis.multilang.MultiLangDaemon'
            print(get_kcl_app_command(args.java, multi_lang_daemon_class, args.properties, paths=args.paths))
        else:
            sys.stderr.write("Must provide arguments: --java and --properties\n")
            parser.print_usage()
    else:
        parser.print_usage()
