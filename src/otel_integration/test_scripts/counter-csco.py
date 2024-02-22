import os
from typing import Sequence

from otel_integration.test_scripts.lib import count_up_it
from otel_integration.util import IntegrationTest, Telemetry, save_telemetry

service_name = 'cop-integration-test'
os.environ['OTEL_SERVICE_NAME'] = service_name

num_adds = 24
count_up_it(num_adds)


class CiscoIntegrationTest(IntegrationTest):

    def is_enabled(self) -> bool:
        return True

    def requirements(self) -> Sequence[str]:
        return ('../..',)

    def wrapper(self) -> str:
        return 'cisco-instrument'

    def validate(self, t: Telemetry) -> None:
        save_telemetry(t, 'csco.json')
        assert_trace_service_name(t.get_traces(), service_name)
        assert num_adds == t.first_sum_value()
        assert num_adds == t.num_traces()

    def should_teardown(self) -> bool:
        return True


def assert_trace_service_name(traces, svc_name):
    for trace in traces:
        assert trace.resourceSpans[0].resource.attributes['serviceName'] == svc_name
