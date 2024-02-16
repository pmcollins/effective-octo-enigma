import glob
import importlib
import os

from otelserver import OtlpGrpcServer

from tests.utils import AccumulatingHandler, Venv

TEST_SCRIPTS_DIR = 'integration_test_scripts'


class ScriptRunner:

    def __init__(self, test_scripts_dir: str):
        self.test_scripts_dir = test_scripts_dir

    def eval_all(self):
        for path in glob.glob('*.py', root_dir=self.test_scripts_dir):
            print(f'Evaluating {path}')
            self.eval_one(path)

    def eval_one(self, script):
        se = ScriptExecution(self.test_scripts_dir, script)
        se.start_test_otlp_listener()
        se.create_venv()
        se.run_script()
        se.cleanup()
        se.validate()


class ScriptExecution:

    def __init__(self, test_scripts_dir: str, script: str, venv_dir: str = "_test_venv"):
        self.test_scripts_dir = test_scripts_dir
        self.script = script

        self.venv = Venv(venv_dir)
        self.handler = AccumulatingHandler()
        self.svr = OtlpGrpcServer(self.handler)

    def start_test_otlp_listener(self):
        self.svr.start()

    def create_venv(self):
        self.venv.create()
        self.venv.run('pip', 'install', '..')

    def run_script(self):
        script_path = os.path.join(self.test_scripts_dir, self.script)
        self.venv.run('cisco-instrument', 'python', script_path)

    def cleanup(self):
        self.venv.delete()
        self.svr.stop()

    def validate(self):
        module_name = '.'.join(['tests', self.test_scripts_dir, self.script[:-3]])
        script_module = importlib.import_module(module_name)
        assert script_module.validate(self.handler.telemetry)


runner = ScriptRunner(TEST_SCRIPTS_DIR)
runner.eval_all()
