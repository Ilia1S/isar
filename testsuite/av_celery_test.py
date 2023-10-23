#!/usr/bin/env python3

from seeds import Seeds
from celery_tasks import *


class AvDevTest(Seeds):

    """
    Developer's test

    :avocado: tags=dev,fast,full
    """

    def test_dev_arm32_av(self):
        try:
            self.publish_relevance('yes')
            result = dev_arm32_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_dev_arm64_av(self):
        try:
            self.publish_relevance('yes')
            result = dev_arm64_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_dev_rebuild_av(self):
        try:
            self.publish_relevance('yes')
            result = dev_rebuild_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_dev_run_amd64_bullseye_av(self):
        status, e = self.perform_run(channel='test_dev_rebuild_av',
                                     celery_task=dev_run_amd64_bullseye_cel)
        self.check_status(status, e)

    def test_dev_run_arm64_bullseye_av(self):
        status, e = self.perform_run(channel='test_dev_arm64_av',
                                     celery_task=dev_run_arm64_bullseye_cel)
        self.check_status(status, e)

    def test_dev_run_arm_bullseye_av(self):
        status, e = self.perform_run(channel='test_dev_arm32_av',
                                     celery_task=dev_run_arm_bullseye_cel)
        self.check_status(status, e)


class AvCrossTest(Seeds):

    """
    Start cross build for the defined set of configurations

    :avocado: tags=cross,fast,full
    """

    def test_crossb_av(self):
        try:
            self.publish_relevance('yes')
            result = crossb_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_cross_rpi_av(self):
        result = cross_rpi_cel.delay()
        result.get()


class AvContainerImageTest(Seeds):

    """
    Test containerized images creation

    :avocado: tags=containerbuild,fast,full,container
    """

    def test_container_image_av(self):
        result = container_image_cel.delay()
        result.get()


class AvContainerSdkTest(Seeds):

    """
    Test SDK container image creation

    :avocado: tags=containersdk,fast,full,container
    """

    def test_container_sdk_av(self):
        result = container_sdk_cel.delay()
        result.get()


class AvVmBootTestFast(Seeds):

    """
    Test QEMU image start (fast)

    :avocado: tags=startvm,fast
    """

    def test_arm_bullseye_fast_av(self):
        status, e = self.perform_run(channel='test_crossb_av',
                                     celery_task=arm_bullseye_fast_cel)
        self.check_status(status, e)

    def test_arm_bullseye_example_module_av(self):
        status, e = self.perform_run(
            channel='test_crossb_av',
            celery_task=arm_bullseye_example_module_cel
        )
        self.check_status(status, e)

    def test_arm_bullseye_getty_target_av(self):
        status, e = self.perform_run(
            channel='test_crossb_av',
            celery_task=arm_bullseye_getty_target_cel
        )
        self.check_status(status, e)

    def test_arm_buster_fast_av(self):
        status, e = self.perform_run(channel='test_crossb_av',
                                     celery_task=arm_buster_fast_cel)
        self.check_status(status, e)

    def test_arm_buster_getty_target_fast_av(self):
        status, e = self.perform_run(
            channel='test_crossb_av',
            celery_task=arm_buster_getty_target_fast_cel
        )
        self.check_status(status, e)

    def test_arm_buster_example_module_fast_av(self):
        status, e = self.perform_run(
            channel='test_crossb_av',
            celery_task=arm_buster_example_module_fast_cel
        )
        self.check_status(status, e)

    def test_arm_bookworm_fast_av(self):
        status, e = self.perform_run(channel='test_crossb_av',
                                     celery_task=arm_bookworm_fast_cel)
        self.check_status(status, e)

    def test_arm_bookworm_example_module_av(self):
        status, e = self.perform_run(
            channel='test_crossb_av',
            celery_task=arm_bookworm_example_module_cel
        )
        self.check_status(status, e)

    def test_arm_bookworm_getty_target_av(self):
        status, e = self.perform_run(
            channel='test_crossb_av',
            celery_task=arm_bookworm_getty_target_cel
        )
        self.check_status(status, e)
