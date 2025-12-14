"""Errors for debugger connection.
"""

class DebuggerConnectionError(Exception):
    """Debugger connection error"""

class SpawnError(DebuggerConnectionError):
    """Debugger could not start execution"""

class ReadError(DebuggerConnectionError):
    """Error occurs when reading from debugger"""

class WriteError(DebuggerConnectionError):
    """Error occurs when writing to debugger"""