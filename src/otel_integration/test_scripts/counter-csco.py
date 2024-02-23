import os
import time
from typing import Sequence

from opentelemetry import metrics, trace

from otel_integration.pbutil import get_trace_attr_str
from otel_integration.util import IntegrationTest, Telemetry, save

service_name = 'cop-integration-test'
os.environ['OTEL_SERVICE_NAME'] = service_name

num_adds = 24
counter = metrics.get_meter('my-meter').create_counter('my-counter')
tracer = trace.get_tracer('my-tracer')
for i in range(num_adds):
    with tracer.start_as_current_span('my-span') as span:
        time.sleep(1)
        counter.add(1)


class CiscoIntegrationTest(IntegrationTest):

    def is_enabled(self) -> bool:
        return True

    def requirements(self) -> Sequence[str]:
        return ('../..',)

    def wrapper(self) -> str:
        return 'cisco-instrument'

    def validate(self, t: Telemetry) -> None:
        save(str(t), 'csco.json')
        for tr in t.get_traces():
            found_svc_names = get_trace_attr_str(tr, 'service.name')
            assert service_name == found_svc_names[0]
        assert num_adds == t.first_sum_value()
        assert num_adds == t.num_traces()

    def should_teardown(self) -> bool:
        return True

