import logging
_logger = logging.getLogger(__name__)

import sublime

def show_input(caption, initial_text, on_done, on_cancel = None):
    """
    Shows an input panel and reshows it if validation (on_done callback returning False) fails

    :param caption: Input caption
    :param initial_text: Input initial text
    :param on_done: Callback to be run (with input text as parameter) when applying input
    :               If returning False it will re-show the input dialog
    :param on_cancel: Callback to be run with cancelling
    """

    def _input_callback(text):
        if on_done(text) is False:
            _logger.debug(f"Failed validating input '{text}'.")
            _show_input(caption, initial_text, on_done, on_cancel)
        else:
            _logger.debug(f"Applying input '{text}'.")

    sublime.active_window().show_input_panel(
        caption = caption,
        initial_text = initial_text,
        on_done = _input_callback,
        on_change = None,
        on_cancel = on_cancel
    )
