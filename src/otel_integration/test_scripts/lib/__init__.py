import time

from opentelemetry import metrics, trace


def count_up_it(n):
    counter = metrics.get_meter('my-meter').create_counter('my-counter')
    tracer = trace.get_tracer('my-tracer')
    for i in range(n):
        with tracer.start_as_current_span('my-span') as span:
            time.sleep(1)
            counter.add(1)
