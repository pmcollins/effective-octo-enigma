import time
from typing import Sequence

from opentelemetry import metrics

from tests.util import Telemetry, IntegrationTest, telemetry_to_file

num_adds = 20
meter = metrics.get_meter('my-meter')
counter = meter.create_counter('my-counter')
for i in range(num_adds):
    time.sleep(1)
    counter.add(1)


class CiscoIntegrationTest(IntegrationTest):

    def requirements(self) -> Sequence[str]:
        return ('..',)

    def wrapper(self) -> str:
        return 'cisco-instrument'

    def validate(self, t: Telemetry) -> bool:
        telemetry_to_file(t, 'splk.json')
        return t.first_sum_value() == num_adds
