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


class AvReproTest(Seeds):

    """
    Test cached base repository

    :avocado: tags=repro,full
    """

    def test_repro_signed_av(self):
        result = repro_signed_cel.delay()
        result.get()

    def test_repro_unsigned_av(self):
        result = repro_unsigned_cel.delay()
        result.get()


class AvCcacheTest(Seeds):

    """
    Test rebuild speed improve with ccache

    :avocado: tags=ccache,full
    """

    def test_ccache_rebuild_av(self):
        result = ccache_rebuild_cel.delay()
        result.get()


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
        try:
            result = cross_rpi_cel.delay()
            result.get()
        except:
            self.cancel('KFAIL')


class AvWicTest(Seeds):

    """
    Test creation of wic images

    :avocado: tags=wic,full
    """

    def test_wic_nodeploy_partitions_av(self):
        try:
            self.publish_relevance('yes')
            result = wic_nodeploy_partitions_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_wic_deploy_partitions_av(self):
        status, e = self.perform_run(
            channel='test_wic_nodeploy_partitions_av',
            celery_task=wic_deploy_partitions_cel)
        self.check_status(status, e)


class AvNoCrossTest(Seeds):

    """
    Start non-cross build for the defined set of configurations

    :avocado: tags=nocross,full
    """

    def test_nocrosss_av(self):
        try:
            self.publish_relevance('yes')
            result = nocrosss_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_nocross_rpi_av(self):
        try:
            result = nocross_rpi_cel.delay()
            result.get()
        except:
            self.cancel('KFAIL')

    def test_nocross_sid_av(self):
        try:
            result = nocross_sid_cel.delay()
            result.get()
        except:
            self.cancel('KFAIL')


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


class AvSstateTest(Seeds):

    """
    Test builds with artifacts taken from sstate cache

    :avocado: tags=sstate,full
    """
    def test_sstate_populate_av(self):
        try:
            self.publish_relevance('yes')
            result = sstate_populate_cel.delay()
            result.get()
        finally:
            self.publish_deps(result.status)

    def test_sstate_av(self):
        status, e = self.perform_run(channel='test_sstate_populate_av',
                                     celery_task=sstate_cel)
        self.check_status(status, e)


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


class AvVmBootTestFull(Seeds):

    """
    Test QEMU image start (full)

    :avocado: tags=startvm,full
    """

    def test_arm_bullseye_full_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=arm_bullseye_full_cel)
        self.check_status(status, e)

    def test_arm_buster_full_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=arm_buster_full_cel)
        self.check_status(status, e)

    def test_arm_buster_example_module_full_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=arm_buster_example_module_full_cel
        )
        self.check_status(status, e)

    def test_arm_buster_getty_target_full_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=arm_buster_getty_target_full_cel
        )
        self.check_status(status, e)

    def test_arm64_bullseyed_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=arm64_bullseyed_cel)
        self.check_status(status, e)

    def test_arm64_bullseye_getty_target_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=arm64_bullseye_getty_target_cel
        )
        self.check_status(status, e)

    def test_arm64_bullseye_example_module_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=arm64_bullseye_example_module_cel
        )
        self.check_status(status, e)

    def test_i386_busterd_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=i386_busterd_cel)
        self.check_status(status, e)

    def test_amd64_busterd_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=amd64_busterd_cel)
        self.check_status(status, e)

    def test_amd64_focals_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=amd64_focals_cel)
        self.check_status(status, e)

    def test_amd64_focal_example_module_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=amd64_focal_example_module_cel
        )
        self.check_status(status, e)

    def test_amd64_focal_getty_target_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=amd64_focal_getty_target_cel)
        self.check_status(status, e)

    def test_amd64_bookworms_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=amd64_bookworms_cel)
        self.check_status(status, e)

    def test_arm_bookworm_full_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=arm_bookworm_full_cel)
        self.check_status(status, e)

    def test_i386_bookworms_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=i386_bookworms_cel)
        self.check_status(status, e)

    def test_mipsel_bookworms_av(self):
        status, e = self.perform_run(channel='test_nocrosss_av',
                                     celery_task=mipsel_bookworms_cel)
        self.check_status(status, e)

    def test_mipsel_bookworm_getty_target_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=mipsel_bookworm_getty_target_cel
        )
        self.check_status(status, e)

    def test_mipsel_bookworm_example_module_av(self):
        status, e = self.perform_run(
            channel='test_nocrosss_av',
            celery_task=mipsel_bookworm_example_module_cel
        )
        self.check_status(status, e)
