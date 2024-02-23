from typing import Optional

from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

from otel_integration.pbutil import get_trace_attr_str


def test_get_trace_attr_str():
    tr = trace()
    matches = get_trace_attr_str(tr, 'telemetry.sdk.language')
    assert 'python' == matches[0]


def metrics():
    with open('fixtures/metrics.pbstr', 'rb') as file:
        read = file.read()
        request = ExportMetricsServiceRequest()
        request.ParseFromString(read)
        return request


def trace():
    with open('fixtures/trace.pbstr', 'rb') as file:
        request = ExportTraceServiceRequest()
        request.ParseFromString(file.read())
        return request

