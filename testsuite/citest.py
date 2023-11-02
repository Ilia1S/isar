#!/usr/bin/env python3

import os

from avocado import skipUnless
from avocado.utils import path
from cibase import CIBaseTest

UMOCI_AVAILABLE = True
SKOPEO_AVAILABLE = True
try:
    path.find_command('umoci')
except path.CmdNotFoundError:
    UMOCI_AVAILABLE = False
try:
    path.find_command('skopeo')
except path.CmdNotFoundError:
    SKOPEO_AVAILABLE = False


class DevTest(CIBaseTest):

    """
    Developer's test

    :avocado: tags=dev,fast,full
    """

    def test_dev_arm32(self):
        targets = ['mc:qemuarm-bullseye:isar-image-base',
                   'mc:qemuarm-bullseye:isar-image-base:do_populate_sdk']
        self.init()
        self.perform_build_test(targets, image_install="example-raw")
        if not self.sequential():
            self.copy_build_dir()

    def test_dev_arm64(self):
        targets = ['mc:qemuarm64-bullseye:isar-image-base']
        self.init()
        self.perform_build_test(targets)
        if not self.sequential():
            self.copy_build_dir()

    def test_dev_rebuild(self):
        targets = ['mc:qemuamd64-bullseye:isar-image-ci']
        self.init()
        self.perform_build_test(targets)
        layerdir_core = self.getVars('LAYERDIR_core')

        dpkgbase_file = layerdir_core + '/classes/dpkg-base.bbclass'

        self.backupfile(dpkgbase_file)
        with open(dpkgbase_file, 'a') as file:
            file.write('do_fetch:append() {\n\n}')
        try:
            self.perform_build_test(targets)
        finally:
            self.restorefile(dpkgbase_file)

        if not self.sequential():
            self.copy_build_dir()

    def test_dev_run_amd64_bullseye(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_dev_rebuild', arch='amd64')
        self.vm_start('amd64', 'bullseye', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_dev_run_arm64_bullseye(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_dev_arm64', arch='arm64',
                                     image='isar-image-base')
        self.vm_start('arm64', 'bullseye')
        if not self.sequential():
            self.copy_build_dir()

    def test_dev_run_arm_bullseye(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_dev_arm32', image='isar-image-base')
        self.vm_start('arm', 'bullseye', skip_modulecheck=True)
        if not self.sequential():
            self.copy_build_dir()


class ReproTest(CIBaseTest):

    """
    Test cached base repository

    :avocado: tags=repro,full
    """

    def test_repro_signed(self):
        targets = [
            'mc:rpi-arm-v7-bullseye:isar-image-base',
            'mc:rpi-arm64-v8-bullseye:isar-image-base',
            'mc:qemuarm64-bullseye:isar-image-base',
                  ]

        self.init()
        try:
            self.perform_repro_test(targets, signed=True)
        finally:
            self.move_in_build_dir('tmp', 'tmp_repro_signed')

        if not self.sequential():
            self.copy_build_dir()

    def test_repro_unsigned(self):
        targets = [
            'mc:qemuamd64-bullseye:isar-image-base',
            'mc:qemuarm-bullseye:isar-image-base',
                  ]

        self.init()
        try:
            self.perform_repro_test(targets, cross=False)
        finally:
            self.move_in_build_dir('tmp', 'tmp_repro_unsigned')

        if not self.sequential():
            self.copy_build_dir()


class CcacheTest(CIBaseTest):

    """
    Test rebuild speed improve with ccache

    :avocado: tags=ccache,full
    """

    def test_ccache_rebuild(self):
        targets = ['mc:qemuamd64-bullseye:hello-isar']
        self.init()
        self.perform_ccache_test(targets)
        if not self.sequential():
            self.copy_build_dir()


class CrossTest(CIBaseTest):

    """
    Start cross build for the defined set of configurations

    :avocado: tags=cross,fast,full
    """

    def test_crossb(self):
        targets = [
            'mc:qemuarm-buster:isar-image-ci',
            'mc:qemuarm-bullseye:isar-image-ci',
            'mc:de0-nano-soc-bullseye:isar-image-base',
            'mc:stm32mp15x-bullseye:isar-image-base',
            'mc:qemuarm-bookworm:isar-image-ci',
            'mc:qemuarm64-bookworm:isar-image-ci',
            'mc:qemuarm64-focal:isar-image-base',
            'mc:nanopi-neo-efi-bookworm:isar-image-base',
                  ]

        self.init()
        self.perform_build_test(targets, debsrc_cache=True)
        if not self.sequential():
            self.copy_build_dir()

    def test_cross_rpi(self):
        targets = [
            'mc:rpi-arm-v7-bullseye:isar-image-base',
                  ]

        self.init()
        try:
            self.perform_build_test(targets, debsrc_cache=True)
        except Exception:
            self.cancel('KFAIL')

        if not self.sequential():
            self.copy_build_dir()


class WicTest(CIBaseTest):

    """
    Test creation of wic images

    :avocado: tags=wic,full
    """

    def test_wic_nodeploy_partitions(self):
        targets = ['mc:qemuarm64-bookworm:isar-image-ci']

        self.init(build_dir='test_wic')
        self.perform_wic_partition_test(targets,
            wic_deploy_parts=False, debsrc_cache=True, compat_arch=False)

        if not self.sequential():
            self.copy_build_dir()

        self.publish_queue('wic')

    def test_wic_deploy_partitions(self):
        self.init(build_dir='test_wic')
        self.define_upstream_test_server('wic')
           
        targets = ['mc:qemuarm64-bookworm:isar-image-ci']

        # reuse artifacts
        self.perform_wic_partition_test(targets,
            wic_deploy_parts=True, debsrc_cache=True, compat_arch=False)

        if not self.sequential():
            self.copy_build_dir()


class NoCrossTest(CIBaseTest):

    """
    Start non-cross build for the defined set of configurations

    :avocado: tags=nocross,full
    """

    def test_nocrosss(self):
        targets = [
            'mc:qemuarm-buster:isar-image-ci',
            'mc:qemuarm-bullseye:isar-image-base',
            'mc:qemuarm64-bullseye:isar-image-ci',
            'mc:qemui386-buster:isar-image-base',
            'mc:qemui386-bullseye:isar-image-base',
            'mc:qemuamd64-buster:isar-image-ci',
            'mc:qemuamd64-bullseye:isar-initramfs',
            'mc:qemumipsel-buster:isar-image-base',
            'mc:qemumipsel-bullseye:isar-image-base',
            'mc:imx6-sabrelite-bullseye:isar-image-base',
            'mc:phyboard-mira-bullseye:isar-image-base',
            'mc:hikey-bullseye:isar-image-base',
            'mc:virtualbox-bullseye:isar-image-base',
            'mc:virtualbox-bookworm:isar-image-base',
            'mc:bananapi-bullseye:isar-image-base',
            'mc:bananapi-bookworm:isar-image-base',
            'mc:nanopi-neo-bullseye:isar-image-base',
            'mc:nanopi-neo-bookworm:isar-image-base',
            'mc:stm32mp15x-bullseye:isar-image-base',
            'mc:qemuamd64-focal:isar-image-ci',
            'mc:qemuamd64-bookworm:isar-image-ci',
            'mc:qemuarm-bookworm:isar-image-ci',
            'mc:qemui386-bookworm:isar-image-base',
            'mc:qemumipsel-bookworm:isar-image-ci',
            'mc:hikey-bookworm:isar-image-base',
            'mc:de0-nano-soc-bookworm:isar-image-base',
                  ]

        self.init()
        self.perform_build_test(targets, cross=False, debsrc_cache=True)
        if not self.sequential():
            self.copy_build_dir()

    def test_nocross_rpi(self):
        targets = [
            'mc:rpi-arm-bullseye:isar-image-base',
            'mc:rpi-arm-v7-bullseye:isar-image-base',
            'mc:rpi-arm-v7l-bullseye:isar-image-base',
            'mc:rpi-arm64-v8-bullseye:isar-image-base',
            'mc:rpi-arm-bookworm:isar-image-base',
            'mc:rpi-arm-v7-bookworm:isar-image-base',
            'mc:rpi-arm-v7l-bookworm:isar-image-base',
            'mc:rpi-arm64-v8-bookworm:isar-image-base',
                  ]

        self.init()
        try:
            self.perform_build_test(targets, cross=False, debsrc_cache=True)
        except Exception:
            self.cancel('KFAIL')

        if not self.sequential():
            self.copy_build_dir()

    def test_nocross_sid(self):
        targets = [
            'mc:qemuriscv64-sid:isar-image-base',
            'mc:sifive-fu540-sid:isar-image-base',
            'mc:starfive-visionfive2-sid:isar-image-base',
                  ]

        self.init()
        try:
            self.perform_build_test(targets, cross=False)
        except Exception:
            self.cancel('KFAIL')

        if not self.sequential():
            self.copy_build_dir()


class ContainerImageTest(CIBaseTest):

    """
    Test containerized images creation

    :avocado: tags=containerbuild,fast,full,container
    """
    @skipUnless(UMOCI_AVAILABLE and SKOPEO_AVAILABLE, 'umoci/skopeo not found')
    def test_container_image(self):
        targets = [
            'mc:container-amd64-buster:isar-image-base',
            'mc:container-amd64-bullseye:isar-image-base',
            'mc:container-amd64-bookworm:isar-image-base',
                  ]

        self.init()
        self.perform_build_test(targets, container=True)
        if not self.sequential():
            self.copy_build_dir()


class ContainerSdkTest(CIBaseTest):

    """
    Test SDK container image creation

    :avocado: tags=containersdk,fast,full,container
    """
    @skipUnless(UMOCI_AVAILABLE and SKOPEO_AVAILABLE, 'umoci/skopeo not found')
    def test_container_sdk(self):
        targets = ['mc:container-amd64-bullseye:isar-image-base']

        self.init()
        self.perform_build_test(targets, bitbake_cmd='do_populate_sdk', container=True)
        if not self.sequential():
            self.copy_build_dir()


class SstateTest(CIBaseTest):

    """
    Test builds with artifacts taken from sstate cache

    :avocado: tags=sstate,full
    """

    def test_sstate_populate(self):
        image_target = 'mc:qemuamd64-bullseye:isar-image-base'

        self.perform_sstate_populate(image_target)

        if not self.sequential():
            self.copy_build_dir()

        self.publish_queue('sstate')

    def test_sstates(self):
        image_target = 'mc:qemuamd64-bullseye:isar-image-base'
        package_target = 'mc:qemuamd64-bullseye:hello'

        self.init(build_dir='build-sstate')
        self.define_upstream_test_server('sstate')
        self.perform_sstate_test(image_target, package_target)

        if not self.sequential():
            self.copy_build_dir()


class SingleTest(CIBaseTest):

    """
    Single test for selected target

    :avocado: tags=single
    """

    def test_single_build(self):
        self.init()
        machine = self.params.get('machine', default='qemuamd64')
        distro = self.params.get('distro', default='bullseye')
        image = self.params.get('image', default='isar-image-base')

        self.perform_build_test(f'mc:{machine}-{distro}:{image}')

    def test_single_run(self):
        self.init()
        machine = self.params.get('machine', default='qemuamd64')
        distro = self.params.get('distro', default='bullseye')

        self.vm_start(machine.removeprefix('qemu'), distro)

class SourceTest(CIBaseTest):

    """
    Source contents test

    :avocado: tags=source
    """
    def test_source(self):
        targets = [
            'mc:qemuamd64-bookworm:libhello',
            'mc:qemuarm64-bookworm:libhello',
                  ]

        self.init()
        self.perform_source_test(targets)


class VmBootTestFast(CIBaseTest):

    """
    Test QEMU image start (fast)

    :avocado: tags=startvm,fast
    """

    def test_arm_bullseye_fast(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb')
        if self.sequential():
            self.vm_start('arm', 'bullseye', image='isar-image-ci', keep=True)
        else:
            self.vm_start('arm', 'bullseye', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_bullseye_example_module(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb')
        if self.sequential():
            self.vm_start('arm', 'bullseye', image='isar-image-ci',
                          cmd='lsmod | grep example_module', keep=True)
        else:
            self.vm_start('arm', 'bullseye', image='isar-image-ci',
                          cmd='lsmod | grep example_module')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_bullseye_getty_target(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb')
        self.vm_start('arm', 'bullseye', image='isar-image-ci',
                      script='test_systemd_unit.sh getty.target 10')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_buster_fast(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb', distro='buster')
        if self.sequential():
            self.vm_start('arm', 'buster', image='isar-image-ci', keep=True)
        else:
            self.vm_start('arm', 'buster', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_buster_getty_target_fast(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb', distro='buster')
        if self.sequential():
            self.vm_start('arm', 'buster', image='isar-image-ci',
                          cmd='systemctl is-active getty.target', keep=True)
        else:
            self.vm_start('arm', 'buster', image='isar-image-ci',
                          cmd='systemctl is-active getty.target')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_buster_example_module_fast(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb', distro='buster')
        self.vm_start('arm', 'buster', image='isar-image-ci',
                      script='test_kernel_module.sh example_module')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_bookworm_fast(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb', distro='bookworm')
        if self.sequential():
            self.vm_start('arm', 'bookworm', image='isar-image-ci', keep=True)
        else:
            self.vm_start('arm', 'bookworm', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_bookworm_example_module(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb', distro='bookworm')
        if self.sequential():
            self.vm_start('arm', 'bookworm', image='isar-image-ci',
                          cmd='lsmod | grep example_module', keep=True)
        else:
            self.vm_start('arm', 'bookworm', image='isar-image-ci',
                          cmd='lsmod | grep example_module')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_bookworm_getty_target(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_crossb', distro='bookworm')
        self.vm_start('arm', 'bookworm', image='isar-image-ci',
                      script='test_systemd_unit.sh getty.target 10')
        if not self.sequential():
            self.copy_build_dir()


class VmBootTestFull(CIBaseTest):

    """
    Test QEMU image start (full)

    :avocado: tags=startvm,full
    """

    def test_arm_bullseye_full(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', image='isar-image-base')
        self.vm_start('arm', 'bullseye')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_buster_full(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', distro='buster')
        if self.sequential():
            self.vm_start('arm', 'buster', image='isar-image-ci', keep=True)
        else:
            self.vm_start('arm', 'buster', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_buster_example_module_full(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', distro='buster')
        if self.sequential():
            self.vm_start('arm', 'buster', image='isar-image-ci',
                          cmd='lsmod | grep example_module', keep=True)
        else:
            self.vm_start('arm', 'buster', image='isar-image-ci',
                          cmd='lsmod | grep example_module')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_buster_getty_target_full(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', distro='buster')
        self.vm_start('arm', 'buster', image='isar-image-ci',
                      script='test_systemd_unit.sh getty.target 10')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm64_bullseyed(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='arm64')
        if self.sequential():
            self.vm_start('arm64', 'bullseye', image='isar-image-ci',
                          keep=True)
        else:
            self.vm_start('arm64', 'bullseye', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm64_bullseye_getty_target(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='arm64')
        if self.sequential():
            self.vm_start('arm64', 'bullseye', image='isar-image-ci',
                          cmd='systemctl is-active getty.target', keep=True)
        else:
            self.vm_start('arm64', 'bullseye', image='isar-image-ci',
                          cmd='systemctl is-active getty.target')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm64_bullseye_example_module(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='arm64')
        self.vm_start('arm64', 'bullseye', image='isar-image-ci',
                      script='test_kernel_module.sh example_module')
        if not self.sequential():
            self.copy_build_dir()

    def test_i386_busterd(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='i386',
                                     distro='buster', image='isar-image-base')
        self.vm_start('i386', 'buster')
        if not self.sequential():
            self.copy_build_dir()

    def test_amd64_busterd(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='amd64',
                                     distro='buster')
        # test efi boot
        self.vm_start('amd64','buster', image='isar-image-ci')
        # test pcbios boot
        self.vm_start('amd64', 'buster', True, image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_amd64_focals(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='amd64',
                                     distro='focal')
        if self.sequential():
            self.vm_start('amd64', 'focal', image='isar-image-ci', keep=True)
        else:
            self.vm_start('amd64', 'focal', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_amd64_focal_example_module(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='amd64',
                                     distro='focal')
        if self.sequential():
            self.vm_start('amd64', 'focal', image='isar-image-ci',
                          cmd='lsmod | grep example_module', keep=True)
        else:
            self.vm_start('amd64', 'focal', image='isar-image-ci',
                          cmd='lsmod | grep example_module')
        if not self.sequential():
            self.copy_build_dir()

    def test_amd64_focal_getty_target(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='amd64',
                                     distro='focal')
        self.vm_start('amd64', 'focal', image='isar-image-ci',
                      script='test_systemd_unit.sh getty.target 10')
        if not self.sequential():
            self.copy_build_dir()

    def test_amd64_bookworms(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='amd64',
                                     distro='bookworm')
        self.vm_start('amd64', 'bookworm', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_arm_bookworm_full(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', distro='bookworm')
        self.vm_start('arm', 'bookworm', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_i386_bookworms(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='i386',
                                     distro='bookworm',
                                     image='isar-image-base')
        self.vm_start('i386', 'bookworm')
        if not self.sequential():
            self.copy_build_dir()

    def test_mipsel_bookworms(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='mipsel',
                                     distro='bookworm')
        if self.sequential():
            self.vm_start('mipsel', 'bookworm', image='isar-image-ci',
                          keep=True)
        else:
            self.vm_start('mipsel', 'bookworm', image='isar-image-ci')
        if not self.sequential():
            self.copy_build_dir()

    def test_mipsel_bookworm_getty_target(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='mipsel',
                                     distro='bookworm')
        if self.sequential():
            self.vm_start('mipsel', 'bookworm', image='isar-image-ci',
                          cmd='systemctl is-active getty.target', keep=True)
        else:
            self.vm_start('mipsel', 'bookworm', image='isar-image-ci',
                          cmd='systemctl is-active getty.target')
        if not self.sequential():
            self.copy_build_dir()

    def test_mipsel_bookworm_example_module(self):
        self.init()
        if not self.check_path():
            self.copy_images_for_run('test_nocrosss', arch='mipsel',
                                     distro='bookworm')
        self.vm_start('mipsel', 'bookworm', image='isar-image-ci',
                      script='test_kernel_module.sh example_module')
