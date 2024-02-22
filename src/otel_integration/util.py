import abc
import json
import os
import shutil
import subprocess
import venv
from typing import Optional

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from otelserver import OtlpRequestHandlerABC


class Telemetry:

    def __init__(self):
        self.logs: Pb2Collection = Pb2Collection()
        self.metrics: Pb2Collection = Pb2Collection()
        self.trace: Pb2Collection = Pb2Collection()

    def add_log(self, log: ExportLogsServiceRequest):
        self.logs.append(log)

    def add_metric(self, metric: ExportMetricsServiceRequest):
        self.metrics.append(metric)

    def add_trace(self, trace: ExportTraceServiceRequest):
        self.trace.append(trace)

    def first_sum_value(self) -> Optional[int]:
        if not self.num_metrics():
            return None
        return self.metrics.get(0).resource_metrics[0].scope_metrics[0].metrics[0].sum.data_points[0].as_int

    def get_traces(self):
        return self.trace.as_list()

    def num_metrics(self) -> int:
        return self.metrics.len()

    def num_traces(self) -> int:
        return self.trace.len()

    def to_dict(self):
        return {
            "logs": self.logs.to_dict(),
            "metrics": self.metrics.to_dict(),
            "trace": self.trace.to_dict(),
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.to_json()


class Pb2Collection:

    def __init__(self):
        self.messages = []

    def as_list(self):
        return self.messages

    def append(self, pb2obj):
        self.messages.append(pb2obj)

    def to_dict(self):
        return [MessageToDict(m) for m in self.messages]

    def to_json(self):
        return json.dumps(self.to_dict())

    def get(self, idx):
        return self.messages[idx]

    def len(self):
        return len(self.messages)


def save_telemetry(telemetry: Telemetry, filename: str) -> None:
    with open(filename, 'w') as file:
        file.write(str(telemetry))


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
        """Throws CalledProcessError"""
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


class IntegrationTest(abc.ABC):

    @abc.abstractmethod
    def is_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def requirements(self) -> list[str]:
        pass

    @abc.abstractmethod
    def wrapper(self) -> str:
        pass

    @abc.abstractmethod
    def validate(self, t: Telemetry) -> None:
        pass

    @abc.abstractmethod
    def should_teardown(self) -> bool:
        pass
