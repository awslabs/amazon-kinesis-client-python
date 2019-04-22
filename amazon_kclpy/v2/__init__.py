# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
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
"""
