import glob
import importlib
import inspect
import os
import logging
from pathlib import Path
from subprocess import CompletedProcess, CalledProcessError

from otelserver import OtlpGrpcServer

from otel_integration.util import Venv, AccumulatingHandler, IntegrationTest

SCRIPT_DIR_NAME = 'test_scripts'


class IntegrationTestRunner:

    def __init__(self, test_scripts_dir: str, logger):
        self.test_scripts_dir = test_scripts_dir
        self.logger = logger

    def eval_all(self):
        for script_name in glob.glob('*.py', root_dir=self.test_scripts_dir):
            self.logger.info(f'Testing {script_name}')
            self.eval_one(script_name)

    def eval_one(self, script_name):
        venv_dir = script_name_to_venv_dir(script_name)
        execution = ScriptExecution(self.test_scripts_dir, script_name, self.logger, venv_dir=venv_dir)
        if not execution.script_is_enabled():
            self.logger.info(f'Skipping disabled script {script_name}')
            return
        execution.start_otlp_listener()
        execution.set_up_venv()
        result = None
        try:
            result = execution.run_script()
        except CalledProcessError as e:
            self.logger.exception(f'Failed to run script {script_name}: {e}')
        finally:
            if result is not None:
                self.logger.info(result.stdout)
            execution.stop_server()
            if execution.script_should_teardown():
                execution.delete_venv()
            execution.validate()


def script_name_to_venv_dir(script):
    return '_venv_' + script[:-3]


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

    def script_is_enabled(self):
        return self.integration_test.is_enabled()

    def script_should_teardown(self):
        return self.integration_test.should_teardown()

    def get_integration_test_class(self):
        module = self.import_module()
        for attr_name in dir(module):
            value = getattr(module, attr_name)
            if inspect.isclass(value) and issubclass(value, IntegrationTest) and value is not IntegrationTest:
                return value

    def import_module(self):
        module_name = '.'.join(['otel_integration', self.test_scripts_dir, self.script[:-3]])
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

    def run_script(self) -> CompletedProcess[str]:
        """Throws CalledProcessError"""
        script_path = os.path.join(self.test_scripts_dir, self.script)
        cmd = ['python', script_path]
        wrapper_script = self.integration_test.wrapper()
        if wrapper_script:
            cmd.insert(0, wrapper_script)
        return self.venv_run(*cmd)

    def venv_run(self, *cmd_plus_args) -> CompletedProcess[str]:
        """Throws CalledProcessError"""
        self.logger.info(f'venv % {" ".join(cmd_plus_args)}')
        return self.venv.run(*cmd_plus_args)

    def stop_server(self):
        self.svr.stop()

    def delete_venv(self):
        self.venv.delete()

    def validate(self):
        self.integration_test.validate(self.handler.telemetry)


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    runner = IntegrationTestRunner(SCRIPT_DIR_NAME, logger)
    runner.eval_all()


def get_scripts_dir():
    parent_dir = Path(__file__).parent.absolute()
    return str(parent_dir / SCRIPT_DIR_NAME)


if __name__ == '__main__':
    main()
