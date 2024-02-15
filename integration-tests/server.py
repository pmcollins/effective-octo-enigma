from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from otelserver import OtlpRequestHandlerABC


class RequestHandler(OtlpRequestHandlerABC):

    def handle_logs(self, request: ExportLogsServiceRequest, context):
        pass

    def handle_metrics(self, request: ExportMetricsServiceRequest, context):
        pass

    def handle_trace(self, request: ExportTraceServiceRequest, context):
        pass
