import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.distro import BaseDistro
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


class CscoDistro(BaseDistro):
    """
    This class is referenced by the entry point opentelemetry_distro:

    [project.entry-points.opentelemetry_distro]
    distro = "csco_otel_python.distro:CscoDistro"
    """

    def _configure(self, **kwargs):
        print('CscoDistro::_configure() running')
        _configure_tracing()
        _configure_metrics()


def _configure_tracing():
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)


def _configure_metrics():
    exporter = OTLPMetricExporter()
    reader = PeriodicExportingMetricReader(exporter)
    meter_provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
