import os

from opentelemetry.instrumentation.distro import BaseDistro


class CscoDistro(BaseDistro):

    def _configure(self, **kwargs):
        print('configuring!!!!!! xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
