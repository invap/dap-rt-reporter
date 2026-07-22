class DAPReporterError(Exception):
    """DAP Reporter error"""


class ReporterInitError(DAPReporterError):
    """Reporter could not be initialized"""


class MessageKeyError(DAPReporterError):
    """Missing key in DAP message"""


class ExecutionError(DAPReporterError):
    """An error occurred during program execution"""


class SetupError(DAPReporterError):
    """Could not set up breakpoint locations"""


class MultipleDebuggerConnectionError(DAPReporterError):
    """Only one debugger connection is allowed"""


class MultipleEventWriterError(DAPReporterError):
    """Only one event writer is allowed"""


class ReporterBuildError(DAPReporterError):
    """Reporter could not build reporter"""
