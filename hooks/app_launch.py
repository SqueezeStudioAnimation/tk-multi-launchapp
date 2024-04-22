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
import tank
import subprocess


class AppLaunch(tank.Hook):
    """
    Hook to run an application.
    """

    def check_rez(self, strict=True):
        """
        Checks to see if a Rez package is available in the current environment.
        If it is available, add it to the system path, exposing the Rez Python API
        :param strict: (bool) If True, raise an error if Rez is not available as a package.
                              This will prevent the app from being launched.
        :returns: A path to the Rez package.
        """

        system = sys.platform

        if system == "win32":
            rez_cmd = 'rez-env rez -- echo %REZ_REZ_ROOT%'
        else:
            rez_cmd = 'rez-env rez -- printenv REZ_REZ_ROOT'

        process = subprocess.Popen(rez_cmd, stdout=subprocess.PIPE, shell=True)
        rez_path, err = process.communicate()

        if err or not rez_path:
            if strict:
                raise ImportError("Failed to find Rez as a package in the current "
                                  "environment! Try 'rez-bind rez'!")
            else:
                print >> sys.stderr, ("WARNING: Failed to find a Rez package in the current "
                                      "environment. Unable to request Rez packages.")

            rez_path = ""
        else:
            rez_path = rez_path.strip()
            print "Found Rez:", rez_path
            print "Adding Rez to system path..."
            sys.path.append(rez_path)

        return rez_path

    def execute(self, app_path, app_args, version, packages=None, **kwargs):
        """
        The execute functon of the hook will be called to start the required application

        :param app_path: (str) The path of the application executable
        :param app_args: (str) Any arguments the application may require
        :param version: (str) version of the application being run if set in the
            "versions" settings of the Launcher instance, otherwise None
        :param engine_name (str) The name of the engine associated with the
            software about to be launched.
        :param software_entity: (dict) If set, this is the Software entity that is
            associated with this launch command.

        :returns: (dict) The two valid keys are 'command' (str) and 'return_code' (int).
        """
        system = sys.platform
        shell_type = 'bash'

        if tank.util.is_linux():
            # on linux, we just run the executable directly
            cmd = "%s %s &" % (app_path, app_args)

        elif tank.util.is_macos():
            # If we're on OS X, then we have two possibilities: we can be asked
            # to launch an application bundle using the "open" command, or we
            # might have been given an executable that we need to treat like
            # any other Unix-style command. The best way we have to know whether
            # we're in one situation or the other is to check the app path we're
            # being asked to launch; if it's a .app, we use the "open" command,
            # and if it's not then we treat it like a typical, Unix executable.
            if app_path.endswith(".app"):
                # The -n flag tells the OS to launch a new instance even if one is
                # already running. The -a flag specifies that the path is an
                # application and supports both the app bundle form or the full
                # executable form.
                cmd = 'open -n -a "%s"' % (app_path)
                if app_args:
                    cmd += " --args %s" % app_args
            else:
                cmd = "%s %s &" % (app_path, app_args)

        else:
            # on windows, we run the start command in order to avoid
            # any command shells popping up as part of the application launch.
            cmd = "start /B \"App\" \"%s\" %s" % (app_path, app_args)
            shell_type = 'cmd'

        if packages is not None and self.check_rez():
            from rez.resolved_context import ResolvedContext
            from rez.config import config

            config.parent_variables = ["PYTHONPATH"]
            context = ResolvedContext(packages)

            n_env = os.environ.copy()
            proc = context.execute_shell(
                command=cmd,
                parent_environ=n_env,
                shell=shell_type,
                stdin=False,
                block=False
            )
            exit_code = proc.wait()
            context.print_info(verbosity=True)

        else:
            # run the command to launch the app
            exit_code = os.system(cmd)

        return {"command": cmd, "return_code": exit_code}
