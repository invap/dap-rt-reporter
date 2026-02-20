from typing import Self

from dap_rt_reporter.connection.gdb_connection import GDBConnection
from dap_rt_reporter.connection.lldb_connection import LLDBConnection
from dap_rt_reporter.errors import (
    MultipleEventWriterError,
    ReporterBuildError,
    MultipleDebuggerConnectionError,
)
from dap_rt_reporter.event_writer.file_writer import FileWriter
from dap_rt_reporter.event_writer.rabbitmq_writer import RabbitMQWriter
from dap_rt_reporter.reporter import Reporter


class RTReporterBuilder:
    def __init__(self):
        self.event_writer = None
        self.debugger_connection = None

    def build(self) -> Reporter:
        if self.debugger_connection is None or self.event_writer is None:
            raise ReporterBuildError

        return Reporter(self.event_writer, self.debugger_connection)

    def with_gdb(self, sut: str, args: str) -> Self:
        if self.debugger_connection is not None:
            raise MultipleDebuggerConnectionError

        self.debugger_connection = GDBConnection(sut, args)
        return self

    def with_lldb(self, sut: str, args: str) -> Self:
        if self.debugger_connection is not None:
            raise MultipleDebuggerConnectionError

        self.debugger_connection = LLDBConnection(sut, args)
        return self

    def with_file_writer(
        self,
        output_file: str,
    ) -> Self:
        if self.event_writer is not None:
            raise MultipleEventWriterError

        self.event_writer = FileWriter(output_file)
        return self

    def with_rabbitmq_writer(self) -> Self:
        if self.event_writer is not None:
            raise MultipleEventWriterError

        self.event_writer = RabbitMQWriter()
        return self
