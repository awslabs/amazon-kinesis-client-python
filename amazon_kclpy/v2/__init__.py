# Copied from README, so that this information is also accessible in the sphinx docs.
'''
Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.

This package provides an interface to the KCL MultiLangDaemon. This interface
manages the interaction with the MultiLangDaemon so that developers can focus
on implementing their record processor. A record processor executable typically
looks something like::

    #!env python
    from amazon_kclpy import kcl
    import json, base64

    class RecordProcessor(kcl.RecordProcessorBase):

        def initialize(self, shard_id):
            pass

        def process_records(self, records, checkpointer):
            pass

        def shutdown(self, checkpointer, reason):
            pass

    if __name__ == "__main__":
        kclprocess = kcl.KCLProcess(RecordProcessor())
        kclprocess.run()
'''
