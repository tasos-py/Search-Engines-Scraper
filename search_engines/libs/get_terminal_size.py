## Code taken from https://github.com/chrippa/backports.shutil_get_terminal_size/blob/master/backports/shutil_get_terminal_size/get_terminal_size.py

"""This is a backport of shutil.get_terminal_size from Python 3.3.
The original implementation is in C, but here we use the ctypes and
fcntl modules to create a pure Python version of os.get_terminal_size.
"""

import os
import struct
import sys

from collections import namedtuple

__all__ = ["get_terminal_size"]


terminal_size = namedtuple("terminal_size", "columns lines")

try:
    from ctypes import windll, create_string_buffer, WinError

    _handle_ids = {
        0: -10,
        1: -11,
        2: -12,
    }

    def _get_terminal_size(fd):
        handle = windll.kernel32.GetStdHandle(_handle_ids[fd])
        if handle == 0:
            raise OSError('handle cannot be retrieved')
        if handle == -1:
            raise WinError()
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
        if res:
            res = struct.unpack("hhhhHhhhhhh", csbi.raw)
            left, top, right, bottom = res[5:9]
            columns = right - left + 1
            lines = bottom - top + 1
            return terminal_size(columns, lines)
        else:
            raise WinError()

except ImportError:
    import fcntl
    import termios

    def _get_terminal_size(fd):
        try:
            res = fcntl.ioctl(fd, termios.TIOCGWINSZ, b"\x00" * 4)
        except IOError as e:
            raise OSError(e)
        lines, columns = struct.unpack("hh", res)

        return terminal_size(columns, lines)


def get_terminal_size(fallback=(80, 24)):
    """Get the size of the terminal window.
    For each of the two dimensions, the environment variable, COLUMNS
    and LINES respectively, is checked. If the variable is defined and
    the value is a positive integer, it is used.
    When COLUMNS or LINES is not defined, which is the common case,
    the terminal connected to sys.__stdout__ is queried
    by invoking os.get_terminal_size.
    If the terminal size cannot be successfully queried, either because
    the system doesn't support querying, or because we are not
    connected to a terminal, the value given in fallback parameter
    is used. Fallback defaults to (80, 24) which is the default
    size used by many terminal emulators.
    The value returned is a named tuple of type os.terminal_size.
    """
    # Try the environment first
    try:
        columns = int(os.environ["COLUMNS"])
    except (KeyError, ValueError):
        columns = 0

    try:
        lines = int(os.environ["LINES"])
    except (KeyError, ValueError):
        lines = 0

    # Only query if necessary
    if columns <= 0 or lines <= 0:
        try:
            size = _get_terminal_size(sys.__stdout__.fileno())
        except (NameError, OSError):
            size = terminal_size(*fallback)

        if columns <= 0:
            columns = size.columns
        if lines <= 0:
            lines = size.lines

    return terminal_size(columns, lines)

