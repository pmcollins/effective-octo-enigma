import os
from typing import Sequence

from tests.integration_tests.lib import count_up_it
from tests.util import Telemetry, IntegrationTest, save_telemetry

os.environ['OTEL_SERVICE_NAME'] = 'cop-integration-test'

num_adds = 24
count_up_it(num_adds)


class CiscoIntegrationTest(IntegrationTest):

    def enabled(self) -> bool:
        return True

    def requirements(self) -> Sequence[str]:
        return ('..',)

    def wrapper(self) -> str:
        return 'cisco-instrument'

    def validate(self, t: Telemetry) -> None:
        save_telemetry(t, 'csco.json')
        assert num_adds == t.first_sum_value()
