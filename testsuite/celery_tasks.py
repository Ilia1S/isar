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


@app.task
def crossb_cel():
    subprocess.run('avocado run \
citest.py:CrossTest.test_crossb', check=True, shell=True)


@app.task
def cross_rpi_cel():
    subprocess.run('avocado run \
citest.py:CrossTest.test_cross_rpi', check=True, shell=True)


@app.task
def container_image_cel():
    subprocess.run('avocado run \
citest.py:ContainerImageTest.test_container_image', check=True, shell=True)


@app.task
def container_sdk_cel():
    subprocess.run('avocado run \
citest.py:ContainerSdkTest.test_container_sdk', check=True, shell=True)


@app.task
def arm_bullseye_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bullseye_fast', check=True, shell=True)


@app.task
def arm_bullseye_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bullseye_example_module',
                   check=True, shell=True)


@app.task
def arm_bullseye_getty_target_cel():
    subprocess.run('avocado run \
                   citest.py:VmBootTestFast.test_arm_bullseye_getty_target',
                   check=True, shell=True)


@app.task
def arm_buster_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_buster_fast', check=True, shell=True)


@app.task
def arm_buster_getty_target_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_buster_getty_target',
                   check=True, shell=True)


@app.task
def arm_buster_example_module_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_buster_example_module',
                   check=True, shell=True)


@app.task
def arm_bookworm_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bookworm_fast', check=True, shell=True)


@app.task
def arm_bookworm_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bookworm_example_module',
                   check=True, shell=True)


@app.task
def arm_bookworm_getty_target_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bookworm_getty_target',
                   check=True, shell=True)
