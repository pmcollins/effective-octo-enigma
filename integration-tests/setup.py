import os
import shutil
import subprocess
import venv

from otelserver import OtlpGrpcServer

from server import RequestHandler


def setup():
    venv_dir = '_venv'
    print(f'deleting venv {venv_dir}')
    shutil.rmtree(venv_dir, ignore_errors=True)

    print(f'creating new "{venv_dir}" venv with pip')
    venv.create(venv_dir, with_pip=True)

    print('running pip')
    run_pip(venv_dir)

    handler = RequestHandler()
    svr = OtlpGrpcServer(handler)
    svr.start()

    print('running python')
    run_test(venv_dir)

    svr.stop()


def run_pip(venv_dir):
    pip_executable = os.path.join(venv_dir, 'bin', 'pip')
    result = subprocess.run(
        [pip_executable, 'install', '..'],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f'run_pip: result.stdout: {result.stdout}')


def run_test(venv_dir):
    python_executable = os.path.join(venv_dir, 'bin', 'python')
    result = subprocess.run(
        [python_executable, '--version'],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f'run_python: result.stdout: {result.stdout}')


setup()
