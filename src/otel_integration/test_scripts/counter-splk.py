import os
from typing import Sequence

from otel_integration.pbutil import save_proto
from otel_integration.test_scripts.lib import count_up_it
from otel_integration.util import IntegrationTest, Telemetry

os.environ['OTEL_SERVICE_NAME'] = 'sop-integration-test'

num_adds = 24
count_up_it(num_adds)


class SplunkIntegrationTest(IntegrationTest):

    def is_enabled(self) -> bool:
        return True

    def requirements(self) -> Sequence[str]:
        return ('splunk-opentelemetry[all]',)

    def wrapper(self) -> str:
        return 'splunk-py-trace'

    def validate(self, t: Telemetry) -> None:
        assert num_adds == t.first_sum_value()
        assert num_adds == t.num_traces()

    def should_teardown(self) -> bool:
        return True
