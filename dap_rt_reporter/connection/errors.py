"""Errors for debugger connection.
"""
class DebuggerConnectionError(Exception):
    """Debugger connection error"""

# For lower level debugger interface
class SpawnError(DebuggerConnectionError):
    """Debugger could not start execution"""

class ReadError(DebuggerConnectionError):
    """Error occurs when reading from debugger"""

class WriteError(DebuggerConnectionError):
    """Error occurs when writing to debugger"""

# For specific debugger error
class DAPRequestError(DebuggerConnectionError):
    """Error occurs while sending a DAP request"""

class DAPResponseError(DebuggerConnectionError):
    """Error occurs while reading to get a new
    DAP response or event"""