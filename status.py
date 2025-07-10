import sublime

def error_message(msg):
    sublime.error_message(f"[{__package__.split('.')[0]}] - {msg}")
