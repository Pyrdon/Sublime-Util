import sublime
import sublime_plugin
import os

import logging
_logger = logging.getLogger(__name__)

from .util import json as json_util

def get_name():
    """
    Gets the project name of the current window

    :returns: The project name, None if no project
    """

    try:
        return sublime.active_window().extract_variables()['project_base_name']
    except KeyError as e:
        return None

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
    _logger.debug(f"Opening project '{name}'.")
    win.run_command("open_project_or_workspace", {"file": new_prj_path})
