import sublime
import sublime_plugin
import subprocess
import os
import json

import logging
_logger = logging.getLogger(__name__)

from .util import json as json_util

def get_name(path = None):
    """
    Gets the project name of the current window or a specific sublime-project file

    :param path: Sublime-project file or None if referring to open project in current window
    :returns: The project name, None if no project or file not found
    """

    if path is None:
        try:
            return sublime.active_window().extract_variables()['project_base_name']
        except KeyError as e:
            return None

    return os.path.splitext(os.path.basename(path))[0]

def rename(name):
    """
    Renames the project in the current window

    :param name: The new name

    :raises Exception: Raised if the current window is not a project
    """

    current_name = get_name()
    if current_name is None:
        raise Exception("Not a project.")

    if name == "" or name == current_name:
        return

    win = sublime.active_window()

    ws_path = win.workspace_file_name()
    ws_dir = os.path.dirname(ws_path)

    prj_path = win.project_file_name()
    prj_dir = os.path.dirname(prj_path)

    _logger.info(f"Renaming project '{current_name}' to '{name}'.")

    # Close current project
    _logger.debug(f"Closing project '{current_name}'.")
    sublime.active_window().run_command('close_workspace')

    # Rename files
    _logger.debug(f"Renaming project files.")
    new_ws_path = os.path.join(ws_dir, f"{name}.sublime-workspace")
    os.rename(ws_path, new_ws_path)
    new_prj_path = os.path.join(prj_dir, f"{name}.sublime-project")
    os.rename(prj_path, new_prj_path)

    # Replace all references to the old project file in the workspace file
    json_util.replace_value_in_file(
        new_ws_path, f"{current_name}.sublime-project", f"{name}.sublime-project")

    # Open new project
    open_project(new_prj_path)

def switch(path):
    """
    Switches to a project of a certain path

    :param path: The project to switch to
    """

    path = os.path.abspath(path)

    _logger.debug(f"Switching to project '{get_name(path)}' of path {path}.")

    project_path = sublime.active_window().project_file_name()
    workspace_path = sublime.active_window().workspace_file_name()
    _logger.debug(f"Current project path is {project_path}")

    if path == project_path:
        # A switch to the same project. Handle this explicitly because the project will be not
        # be opened again and the closing of the window will close the project.
        return

    # if path == workspace_path:
    #     # A switch to the same workspace. Handle this explicitly because the project will be not
    #     # be opened again and the closing of the window will close the project.
    #     return

    # Close all windows belonging to the current project, if any
    if project_path is not None:
        for w in list(sublime.windows()):
            if w.project_file_name() == project_path:
                w.run_command("close_window")

    # Open the new project
    sublime.active_window().run_command("open_project_or_workspace", {"file": path})

def open_project(path):
    """
    Opens a project of a certain path

    :param path: The project to open
    """

    _logger.debug(f"Opening project '{get_name(path)}' from path {path}.")
    sublime.active_window().run_command("open_project_or_workspace", {"file": path})
    # subprocess.Popen([sublime.executable_path(), path])

def create(path):
    data = {
        "folders": [
            {
                "path": "."
            }
        ],
        "settings": {
        }
    }

    # Write the project file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
