import os
import subprocess
import yaml

from celery import Celery


yaml_dir = os.path.dirname(os.path.abspath(__file__))
with open(f'{yaml_dir}/server_data.yaml', 'r') as yaml_file:
    yaml_data = yaml.safe_load(yaml_file)
    redis_server = yaml_data['redis_server']
    redis_port = yaml_data['redis_port']

app = Celery('celery_tasks',
             backend=f'redis://{redis_server}:{redis_port}/1',
             broker=f'redis://{redis_server}:{redis_port}/0')
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_transport_options = {'visibility_timeout': 36000}
app.conf.worker_prefetch_multiplier = 1


@app.task
def dev_arm32_cel():
    subprocess.run('avocado run citest.py:DevTest.test_dev_arm32',
                   check=True, shell=True)


@app.task
def dev_arm64_cel():
    subprocess.run('avocado run citest.py:DevTest.test_dev_arm64', check=True,
                   shell=True)


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
def repro_signed_cel():
    subprocess.run('avocado run \
citest.py:ReproTest.test_repro_signed', check=True, shell=True)


@app.task
def repro_unsigned_cel():
    subprocess.run('avocado run \
citest.py:ReproTest.test_repro_unsigned', check=True, shell=True)


@app.task
def ccache_rebuild_cel():
    subprocess.run('avocado run \
citest.py:CcacheTest.test_ccache_rebuild', check=True, shell=True)


@app.task
def crossb_cel():
    subprocess.run('avocado run \
citest.py:CrossTest.test_crossb', check=True, shell=True)


@app.task
def cross_rpi_cel():
    subprocess.run('avocado run \
citest.py:CrossTest.test_cross_rpi', check=True, shell=True)


@app.task
def wic_nodeploy_partitions_cel():
    subprocess.run('avocado run \
citest.py:WicTest.test_wic_nodeploy_partitions', check=True, shell=True)


@app.task
def wic_deploy_partitions_cel():
    subprocess.run('avocado run \
citest.py:WicTest.test_wic_deploy_partitions', check=True, shell=True)


@app.task
def nocrosss_cel():
    subprocess.run('avocado run \
citest.py:NoCrossTest.test_nocrosss', check=True, shell=True)


@app.task
def nocross_rpi_cel():
    subprocess.run('avocado run \
citest.py:NoCrossTest.test_nocross_rpi', check=True, shell=True)


@app.task
def nocross_sid_cel():
    subprocess.run('avocado run \
citest.py:NoCrossTest.test_nocross_sid', check=True, shell=True)


@app.task
def container_image_cel():
    subprocess.run('avocado run \
citest.py:ContainerImageTest.test_container_image', check=True, shell=True)


@app.task
def container_sdk_cel():
    subprocess.run('avocado run \
citest.py:ContainerSdkTest.test_container_sdk', check=True, shell=True)


@app.task
def sstate_populate_cel():
    subprocess.run('avocado run \
citest.py:SstateTest.test_sstate_populate', check=True, shell=True)


@app.task
def sstate_cel():
    subprocess.run('avocado run \
citest.py:SstateTest.test_sstates', check=True, shell=True)


@app.task
def arm_bullseye_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bullseye_fast', check=True, shell=True)


@app.task
def arm_bullseye_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bullseye_example_module', check=True,
                   shell=True)


@app.task
def arm_bullseye_getty_target_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bullseye_getty_target', check=True,
                   shell=True)


@app.task
def arm_buster_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_buster_fast', check=True, shell=True)


@app.task
def arm_buster_getty_target_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_buster_getty_target_fast', check=True,
                   shell=True)


@app.task
def arm_buster_example_module_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_buster_example_module', check=True,
                   shell=True)


@app.task
def arm_bookworm_fast_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bookworm_fast', check=True, shell=True)


@app.task
def arm_bookworm_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bookworm_example_module', check=True,
                   shell=True)


@app.task
def arm_bookworm_getty_target_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFast.test_arm_bookworm_getty_target', check=True,
                   shell=True)


@app.task
def arm_bullseye_full_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm_bullseye_full', check=True, shell=True)


@app.task
def arm_buster_full_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm_buster_full', check=True, shell=True)


@app.task
def arm_buster_example_module_full_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm_buster_example_module_full', check=True,
                   shell=True)


@app.task
def arm_buster_getty_target_full_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm_buster_getty_target_full', check=True,
                   shell=True)


@app.task
def arm64_bullseyed_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm64_bullseyed', check=True, shell=True)


@app.task
def arm64_bullseye_getty_target_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm64_bullseye_getty_target', check=True,
                   shell=True)


@app.task
def arm64_bullseye_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm64_bullseye_example_module', check=True,
                   shell=True)


@app.task
def i386_busterd_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_i386_busterd', check=True, shell=True)


@app.task
def amd64_busterd_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_amd64_busterd', check=True, shell=True)


@app.task
def amd64_focals_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_amd64_focals', check=True, shell=True)


@app.task
def amd64_focal_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_amd64_focal_example_module', check=True,
                   shell=True)


@app.task
def amd64_focal_getty_target_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_amd64_focal_getty_target', check=True,
                   shell=True)


@app.task
def amd64_bookworms_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_amd64_bookworms', check=True, shell=True)


@app.task
def arm_bookworm_full_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_arm_bookworm_full', check=True, shell=True)


@app.task
def i386_bookworms_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_i386_bookworms', check=True, shell=True)


@app.task
def mipsel_bookworms_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_mipsel_bookworms', check=True, shell=True)


@app.task
def mipsel_bookworm_getty_target_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_mipsel_bookworm_getty_target', check=True,
                   shell=True)


@app.task
def mipsel_bookworm_example_module_cel():
    subprocess.run('avocado run \
citest.py:VmBootTestFull.test_mipsel_bookworm_example_module', check=True,
                   shell=True)
