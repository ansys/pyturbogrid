# Copyright (c) 2024 ANSYS, Inc. All rights reserved
#
# A single_blade_row (SBR) instance represents one turbogrid application.
# The application is implicitly linked to others via the parent,
# a multi_blade_row (MBR) instance.
# MBR will spawn SBRs and communicate with them via queues.
# SBRs will communicate back with the parent to answer queries,
# or to represent its running state.
# SBRs are stateful and meaningless without their parent.
# Since SBRs are threads launched by the parent, they inherit from threading.Thread

import threading


class single_blade_row(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass
