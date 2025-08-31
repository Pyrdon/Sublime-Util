import logging
_logger = logging.getLogger(__name__)

from .util import menu
from . import misc
from . import user_input

import sublime
from collections import namedtuple

# Some named tuples for the menu contents to simplfy implementation
_MenuContents = namedtuple('MenuContents', ['title', 'description', 'annotation'])
_MenuItemContents = namedtuple('MenuItemContents', ['title', 'description', 'annotation', 'callback'])

class QuickMenu(menu.Menu):
    """
    A class representing a menu of items (other menus or actions)
    """

    def __init__(self, title = "Top level", description = "", annotation = "", *, cancel_callback = None):
        """
        Initializes the QuickMenu

        :param title: The title
        :param description: The description (shown below the title)
        :param annotation: The annotation (shown to the right)
        :param cancel_callback: A callback run when the menu is cancelled without action
        """

        super().__init__(_MenuContents(title, description, annotation),
            cancel_callback = cancel_callback)

    def add_menu(self, title, description = "", annotation = ""):
        """
        Adds a sub menu

        :param title: The title
        :param description: The description (shown below the title)
        :param annotation: The annotation (shown to the right)

        :returns: The sub QuickMenu
        """

        contents = QuickMenu(title, description, annotation)
        super().add(contents)
        return contents

    def add_callback(self, title, description = "", annotation = "", *, callback):
        """
        Adds an item with a callback

        :param title: The title
        :param description: The description (shown below the title)
        :param annotation: The annotation (shown to the right)
        :param callback: The callback to be run to apply the action
        """

        contents = _QuickItem(title, description, annotation, callback)
        super().add(contents)

    def add_input(self, title, input_caption, input_initial_text, description = "", annotation = "", *, input_callback):
        """
        Adds an item with a request for user input

        :param title: The title of the item
        :param input_caption: The caption of the user input request
        :param input_initial_text: The intitial text to show in the user input request
        :param description: The description of the item (shown below the title)
        :param annotation: The annotation of the item (shown to the right)
        :param input_callback: The callback to be run to validate and apply the results of the
                               given input.
        """

        def _item_callback(item, event):
            def _on_cancel():
                item.back()

            user_input.show_input(
                caption = input_caption,
                initial_text = input_initial_text,
                on_done = lambda text : input_callback(text, event),
                on_cancel = _on_cancel
            )

        contents = _QuickItem(title, description, annotation, _item_callback)
        super().add(contents)

    def add_command(self, title, description = "", annotation = "", *, command):
        """
        Adds a Sublime command as an item in the Menu

        :param title: The title
        :param description: The description (shown below the title)
        :param annotation: The annotation (shown to the right)
        :param command: The Command class or name
        """

        def _command_callback(item):
            if isinstance(command, str):
                name = command
            else:
                name = misc.class_name_to_command(command)

            _logger.debug(f"Executing command '{name}'.")
            sublime.run_command(name)

        contents = _QuickItem(title, description, annotation, _command_callback)
        super().add(contents)
        return contents

    def execute(self, *args, **kwargs):
        """
        Opens the QuickMenu
        """

        _logger.debug(f"Showing QuickMenu {self}, selecting index {self.selected_index}")
        items = []
        for sub_item in self.items:
            items.append(
                sublime.QuickPanelItem(
                    trigger = sub_item.contents.title,
                    details = sub_item.contents.description,
                    annotation = sub_item.contents.annotation
                )
            )

        sublime.active_window().show_quick_panel(
            items = items,
            selected_index = self.selected_index,
            on_select = self._on_select,
            on_highlight = self._on_highlight,
            flags = sublime.QuickPanelFlags.WANT_EVENT
        )

    def cancel(self):
        """
        Closes the QuickMenu
        """

        _logger.debug(f"Closing QuickMenu {self}")

        # Ensure that whatever Sublime is doing is finished and close the panel as soon as possible
        sublime.set_timeout(lambda : sublime.active_window().run_command("hide_overlay"), 0)

    def _on_select(self, index, event):
        """
        Run when user applies an item (presses Enter)

        :param index: The index selected (-1 if cancelling)
        :param event: The event
        """

        if index != -1:
            self.enter(event)
        else:
            self.back()

    def _on_highlight(self, index):
        """
        Run when user changes selection and then updates index of selected item

        :param index: The selected index
        """

        self.select(index)

class _QuickItem(menu.MenuItem):
    """
    An internal-only class representing a menu item (action)
    """

    def __init__(self, title, description, annotation, callback):
        """
        Initializes the menu item

        :param title: The title
        :param description: The description (shown below the title)
        :param annotation: The annotation (shown to the right)
        """

        super().__init__(_MenuItemContents(title, description, annotation, callback))

    @property
    def title(self):
        """
        Property reflecting the title of the item

        :returns: The title
        """

        return self.contents.title

    @property
    def description(self):
        """
        Property reflecting the description of the item

        :returns: The description
        """
        return self.contents.description

    @property
    def annotation(self):
        """
        Property reflecting the annotation of the item

        :returns: The annotation
        """

        return self.contents.annotation

    def execute(self, *args, **kwargs):
        """
        Applies the action of the selected item
        """

        _logger.debug(f"Executing QuickMenu item {self}.")
        self.contents.callback(self, *args, **kwargs)
