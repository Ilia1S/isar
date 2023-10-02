import subprocess

from celery import Celery


app = Celery('celery_tasks', backend='redis://turar:6379/1',
             broker='redis://turar:6379/0')
app.conf.worker_prefetch_multiplier = 1
app.conf.broker_connection_retry_on_startup = True


@app.task
def dev_arm32_cel():
    subprocess.run('avocado run citest.py:DevTest.test_dev_arm32',
                   check=True, shell=True)


@app.task
def dev_arm64_cel():
    subprocess.run('avocado run citest.py:DevTest.test_dev_arm64',
                   check=True, shell=True)


@app.task
def dev_rebuild_cel():
    subprocess.run('avocado run citest.py:DevTest.test_dev_rebuild',
                   check=True, shell=True)


@app.task
def dev_run_amd64_bullseye_cel():
    subprocess.run('avocado run \
citest.py:DevTest.test_dev_run_amd64_bullseye', check=True, shell=True)


@app.task
def dev_run_arm64_bullseye_cel():
    subprocess.run('avocado run \
citest.py:DevTest.test_dev_run_arm64_bullseye', check=True, shell=True)


@app.task
def dev_run_arm_bullseye_cel():
    subprocess.run('avocado run \
citest.py:DevTest.test_dev_run_arm_bullseye', check=True, shell=True)
