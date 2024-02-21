import glob
import importlib
import inspect
import os
import logging

from otelserver import OtlpGrpcServer

from tests.util import AccumulatingHandler, Venv, IntegrationTest

INTEGRATION_TESTS_DIR = 'integration_tests'


class IntegrationTestRunner:

    def __init__(self, test_scripts_dir: str, logger):
        self.test_scripts_dir = test_scripts_dir
        self.logger = logger

    def eval_all(self):
        for path in glob.glob('*.py', root_dir=self.test_scripts_dir):
            self.logger.info(f'Testing {path}')
            self.eval_one(path)

    def eval_one(self, script):
        se = ScriptExecution(self.test_scripts_dir, script, self.logger)
        se.start_otlp_listener()
        se.set_up_venv()
        se.run_script()
        se.cleanup()
        se.validate()


class ScriptExecution:

    def __init__(self, test_scripts_dir: str, script: str, logger, venv_dir: str = "_test_venv"):
        self.test_scripts_dir = test_scripts_dir
        self.script = script
        self.logger = logger

        self.venv = Venv(venv_dir)
        self.handler = AccumulatingHandler()
        self.svr = OtlpGrpcServer(self.handler)

        integration_test_class = self.get_integration_test_class()
        self.integration_test: IntegrationTest = integration_test_class()

    def get_integration_test_class(self):
        module = self.import_module()
        for attr_name in dir(module):
            value = getattr(module, attr_name)
            if inspect.isclass(value) and issubclass(value, IntegrationTest) and value is not IntegrationTest:
                return value

    def import_module(self):
        module_name = '.'.join(['tests', self.test_scripts_dir, self.script[:-3]])
        self.logger.info(f'Importing module {module_name}')
        return importlib.import_module(module_name)

    def start_otlp_listener(self):
        self.logger.info(f'Starting OTLP server')
        self.svr.start()

    def set_up_venv(self):
        self.logger.info(f'Creating venv')
        self.venv.create()
        for req in self.integration_test.requirements():
            self.logger.info(f'Installing requirement: "{req}"')
            self.venv_run('pip', 'install', req)

    def run_script(self):
        script_path = os.path.join(self.test_scripts_dir, self.script)
        cmd = ['python', script_path]
        wrapper_script = self.integration_test.wrapper()
        if wrapper_script:
            cmd.insert(0, wrapper_script)
        self.venv_run(*cmd)

    def venv_run(self, *cmd_plus_args):
        self.logger.info(f'Running in venv: {cmd_plus_args}')
        self.venv.run(*cmd_plus_args)

    def cleanup(self):
        self.logger.info(f'Cleaning up')
        self.venv.delete()
        self.svr.stop()

    def validate(self):
        valid = self.integration_test.validate(self.handler.telemetry)
        self.logger.info(f'Valid: {valid}')
        assert valid


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    runner = IntegrationTestRunner(INTEGRATION_TESTS_DIR, logger)
    runner.eval_all()


if __name__ == '__main__':
    main()
