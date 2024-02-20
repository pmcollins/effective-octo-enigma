import time
from typing import Sequence

from opentelemetry import metrics

from tests.util import Telemetry, ConfigABC

meter = metrics.get_meter('my-meter')
counter = meter.create_counter('my-counter')

num_adds = 20
for i in range(num_adds):
    time.sleep(1)
    counter.add(1)


class Config(ConfigABC):

    def requirements(self) -> Sequence[str]:
        return ('splunk-opentelemetry',)

    def wrapper_name(self) -> str:
        return 'splunk-py-trace'

    def validate(self, t: Telemetry) -> bool:
        count = t.metrics[0].resource_metrics[0].scope_metrics[0].metrics[0].sum.data_points[0].as_int
        return count == num_adds

