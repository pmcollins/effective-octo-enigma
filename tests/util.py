import os
import shutil
import subprocess
import venv

from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from otelserver import OtlpRequestHandlerABC


class Telemetry:

    def __init__(self):
        self.logs = []
        self.metrics = []
        self.trace = []

    def add_log(self, log):
        self.logs.append(log)

    def add_metric(self, metric):
        self.metrics.append(metric)

    def add_trace(self, trace):
        self.trace.append(trace)


class AccumulatingHandler(OtlpRequestHandlerABC):

    def __init__(self):
        self.telemetry = Telemetry()

    def handle_logs(self, request: ExportLogsServiceRequest, context):
        self.telemetry.add_log(request)

    def handle_metrics(self, request: ExportMetricsServiceRequest, context):
        self.telemetry.add_metric(request)

    def handle_trace(self, request: ExportTraceServiceRequest, context):
        self.telemetry.add_trace(request)


class Venv:

    def __init__(self, venv_dir: str):
        self.venv_dir = venv_dir

    def create(self):
        venv.create(self.venv_dir, with_pip=True)

    def run(self, *cmd_plus_args):
        cmd_path = os.path.join(self.venv_dir, 'bin', cmd_plus_args[0])
        return subprocess.run(
            [cmd_path, *cmd_plus_args[1:]],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def delete(self):
        shutil.rmtree(self.venv_dir, ignore_errors=True)
