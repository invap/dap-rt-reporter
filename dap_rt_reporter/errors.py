class DAPReporterError(Exception):
    """DAP Reporter error"""

class ReporterInitError(DAPReporterError):
    """An invalid debugger was selected"""

class ExecutionError(DAPReporterError):
    """An error occured during progran execution"""