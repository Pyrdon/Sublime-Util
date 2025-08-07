import time
from .util import misc

class time_this:
  def __init__(self,txt=''):
    if txt is None:
      self.txt = 'Time: '
    else:
      self.txt = txt+': '

  def __enter__(self,):
    self.start_time = time.time()
    self.start_cpu_time = time.process_time()
    return self

  def __exit__(self, type, value, traceback):
    diff = time.time() - self.start_time
    cpu_diff = time.process_time() - self.start_cpu_time

    s,ms = divmod(diff*1000,1000)
    cs,cms = divmod(cpu_diff*1000,1000)

    print("{}{:.0f}s, {:.0f}ms ({:.0f}s, {:.0f}ms in CPU time)".format(self.txt,s,ms,cs,cms))

def class_name_to_command(cls):
    """
    Converts a Command class to the Sublime command name

    :param cls: The Command class
    :raises ValueError: Raised if Command class name does not end with 'Command'
    :returns: The command name
    """

    name = cls.__name__
    suffix = 'Command'
    if name.endswith(suffix):
        return misc.camel_to_snake(name.removesuffix(suffix))

    raise ValueError(f"Command class ({name}) name must end with '{suffix}'.")
