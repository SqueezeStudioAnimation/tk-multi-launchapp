# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
App Launch Hook

This hook is executed to launch the applications.
"""

import os
import sys
import tank

class AppLaunch(tank.Hook):
    """
    Hook to run an application.
    """

    def execute(self, default_packages=None, **kwargs):
        """
        The execute function of the hook will be called to resolve needed REZ packages for the current context.
        Override this function if you have really specific override do to on a per-entity basis.
        :returns: (dict) The two valid keys are 'command' (str) and 'return_code' (int).
        """
        multi_launchapp = self.parent
        extra = multi_launchapp.get_setting("extra")
        packages = extra.get("rez_packages", default_packages)
        if packages is None:
            packages = []

        # >>> If you really need to do a specific context override, do it here. <<<

        return packages