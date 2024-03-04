#!/usr/bin/env python3

import logging
import os
import pickle
import re
import select
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import time
import tempfile
import yaml

import paramiko
import start_vm

from avocado import Test
from avocado.utils import path
from avocado.utils import process
from avocado.utils import ssh

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../bitbake/lib')

import bb
import bb.tinfoil

DEF_VM_TO_SEC = 600

isar_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backup_prefix = '.ci-backup'

app_log = logging.getLogger("avocado.app")

class CanBeFinished(Exception):
    pass

class CIBuilder(Test):
    def setUp(self):
        super(CIBuilder, self).setUp()
        job_log = os.path.join(os.path.dirname(self.logdir), '..', 'job.log')
        self._file_handler = logging.FileHandler(filename=job_log)
        self._file_handler.setLevel(logging.ERROR)
        fmt = ('%(asctime)s %(module)-16.16s L%(lineno)-.4d %('
               'levelname)-5.5s| %(message)s')
        formatter = logging.Formatter(fmt=fmt)
        self._file_handler.setFormatter(formatter)
        app_log.addHandler(self._file_handler)

    def init(self, build_dir='build', isar_dir=isar_root):
        # initialize build_dir and setup environment
        # needs to run once (per test case)
        if hasattr(self, 'build_dir'):
            self.error("Broken test implementation: init() called multiple times.")
        self.build_dir = os.path.join(isar_dir, build_dir)
        os.chdir(isar_dir)
        os.environ["TEMPLATECONF"] = "meta-test/conf"
        path.usable_rw_dir(self.build_dir)
        output = process.getoutput('/bin/bash -c "source isar-init-build-env \
                                    %s 2>&1 >/dev/null; env"' % self.build_dir)
        env = dict(((x.split('=', 1) + [''])[:2] \
                    for x in output.splitlines() if x != ''))
        os.environ.update(env)

        self.vm_dict = {}
        self.vm_dict_file = '%s/vm_dict_file' % self.build_dir

        if os.path.isfile(self.vm_dict_file):
            with open(self.vm_dict_file, "rb") as f:
                data = f.read()
                if data:
                    self.vm_dict = pickle.loads(data)

    def check_init(self):
        if not hasattr(self, 'build_dir'):
            self.error("Broken test implementation: need to call init().")

    def configure(self, compat_arch=True, cross=True, debsrc_cache=False,
                  container=False, ccache=False, sstate=False, offline=False,
                  gpg_pub_key=None, wic_deploy_parts=False, dl_dir=None,
                  sstate_dir=None, ccache_dir=None,
                  source_date_epoch=None, image_install=None, **kwargs):
        # write configuration file and set bitbake_args
        # can run multiple times per test case
        self.check_init()

        # get parameters from avocado cmdline
        quiet = bool(int(self.params.get('quiet', default=1)))

        if not sstate:
            sstate = bool(int(self.params.get('sstate', default=0)))

        # set those to "" to not set dir value but use system default
        if dl_dir is None:
            dl_dir = os.getenv('DL_DIR')
        if dl_dir is None:
            dl_dir = os.path.join(isar_root, 'downloads')
        if sstate_dir is None:
            sstate_dir = os.getenv('SSTATE_DIR')
        if sstate_dir is None:
            sstate_dir = os.path.join(isar_root, 'sstate-cache')
        if ccache_dir is None:
            ccache_dir = '${TOPDIR}/ccache'

        # get parameters from environment
        distro_apt_premir = os.getenv('DISTRO_APT_PREMIRRORS')

        self.log.info(f'===================================================\n'
                      f'Configuring build_dir {self.build_dir}\n'
                      f'  compat_arch = {compat_arch}\n'
                      f'  cross = {cross}\n'
                      f'  debsrc_cache = {debsrc_cache}\n'
                      f'  offline = {offline}\n'
                      f'  container = {container}\n'
                      f'  ccache = {ccache}\n'
                      f'  sstate = {sstate}\n'
                      f'  gpg_pub_key = {gpg_pub_key}\n'
                      f'  wic_deploy_parts = {wic_deploy_parts}\n'
                      f'  source_date_epoch = {source_date_epoch} \n'
                      f'  dl_dir = {dl_dir}\n'
                      f'  sstate_dir = {sstate_dir}\n'
                      f'  ccache_dir = {ccache_dir}\n'
                      f'  image_install = {image_install}\n'
                      f'===================================================')

        # determine bitbake_args
        self.bitbake_args = []
        if not quiet:
            self.bitbake_args.append('-v')
        if not sstate:
            self.bitbake_args.append('--no-setscene')

        # write ci_build.conf
        with open(self.build_dir + '/conf/ci_build.conf', 'w') as f:
            if compat_arch:
                f.write('ISAR_ENABLE_COMPAT_ARCH:amd64 = "1"\n')
                f.write('IMAGE_INSTALL:remove:amd64 = "hello-isar"\n')
                f.write('IMAGE_INSTALL:append:amd64 = " hello-isar-compat"\n')
                f.write('ISAR_ENABLE_COMPAT_ARCH:arm64 = "1"\n')
                f.write('IMAGE_INSTALL:remove:arm64 = "hello-isar"\n')
                f.write('IMAGE_INSTALL:append:arm64 = " hello-isar-compat"\n')
                f.write('IMAGE_INSTALL += "kselftest"\n')
            if cross:
                f.write('ISAR_CROSS_COMPILE = "1"\n')
            if debsrc_cache:
                f.write('BASE_REPO_FEATURES = "cache-deb-src"\n')
            if offline:
                f.write('ISAR_USE_CACHED_BASE_REPO = "1"\n')
                f.write('BB_NO_NETWORK = "1"\n')
            if container:
                f.write('SDK_FORMATS = "docker-archive"\n')
                f.write('IMAGE_INSTALL:remove = "example-module-${KERNEL_NAME} enable-fsck"\n')
            if gpg_pub_key:
                f.write('BASE_REPO_KEY="file://' + gpg_pub_key + '"\n')
            if wic_deploy_parts:
                f.write('WIC_DEPLOY_PARTITIONS = "1"\n')
            if distro_apt_premir:
                f.write('DISTRO_APT_PREMIRRORS = "%s"\n' % distro_apt_premir)
            if ccache:
                f.write('USE_CCACHE = "1"\n')
                f.write('CCACHE_TOP_DIR = "%s"\n' % ccache_dir)
            if source_date_epoch:
                f.write('SOURCE_DATE_EPOCH = "%s"\n' % source_date_epoch)
            if dl_dir:
                f.write('DL_DIR = "%s"\n' % dl_dir)
            if sstate_dir:
                f.write('SSTATE_DIR = "%s"\n' % sstate_dir)
            if image_install is not None:
                f.write('IMAGE_INSTALL = "%s"' % image_install)

        # include ci_build.conf in local.conf
        with open(self.build_dir + '/conf/local.conf', 'r+') as f:
            for line in f:
                if 'include ci_build.conf' in line:
                    break
            else:
                f.write('\ninclude ci_build.conf')

    def unconfigure(self):
        self.check_init()
        open(self.build_dir + '/conf/ci_build.conf', 'w').close()

    def delete_from_build_dir(self, path):
        self.check_init()
        shutil.rmtree(self.build_dir + '/' + path, True)

    def move_in_build_dir(self, src, dst):
        self.check_init()
        if os.path.exists(self.build_dir + '/' + src):
            shutil.move(self.build_dir + '/' + src, self.build_dir + '/' + dst)

    def bitbake(self, target, bitbake_cmd=None, **kwargs):
        self.check_init()
        self.log.info('===================================================')
        self.log.info('Building ' + str(target))
        self.log.info('===================================================')
        os.chdir(self.build_dir)
        cmdline = ['bitbake']
        if self.bitbake_args:
            cmdline.extend(self.bitbake_args)
        if bitbake_cmd:
            cmdline.append('-c')
            cmdline.append(bitbake_cmd)
        if isinstance(target, list):
            cmdline.extend(target)
        else:
            cmdline.append(target)

        with subprocess.Popen(" ".join(cmdline), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, universal_newlines=True,
                              shell=True) as p1:
            poller = select.poll()
            poller.register(p1.stdout, select.POLLIN)
            poller.register(p1.stderr, select.POLLIN)
            while p1.poll() is None:
                events = poller.poll(1000)
                for fd, event in events:
                    if event != select.POLLIN:
                        continue
                    if fd == p1.stdout.fileno():
                        self.log.info(p1.stdout.readline().rstrip())
                    if fd == p1.stderr.fileno():
                        app_log.error(p1.stderr.readline().rstrip())
            p1.wait()
            if p1.returncode:
                self.fail('Bitbake failed')

    def backupfile(self, path):
        self.check_init()
        try:
            shutil.copy2(path, path + backup_prefix)
        except FileNotFoundError:
            self.log.warn(path + ' not exist')

    def backupmove(self, path):
        self.check_init()
        try:
            shutil.move(path, path + backup_prefix)
        except FileNotFoundError:
            self.log.warn(path + ' not exist')

    def restorefile(self, path):
        self.check_init()
        try:
            shutil.move(path + backup_prefix, path)
        except FileNotFoundError:
            self.log.warn(path + backup_prefix + ' not exist')

    def getVars(self, *vars, target=None):
        self.check_init()
        def fixStream(stream):
            # fix stream objects to emulate _io.TextIOWrapper
            stream.isatty = lambda: False
            stream.fileno = lambda: False
            stream.encoding = sys.getdefaultencoding()

        sl = target is not None
        fixStream(sys.stdout)
        fixStream(sys.stderr)

        # wait until previous bitbake will be finished
        lockfile = os.path.join(self.build_dir, 'bitbake.lock')
        checks = 0
        while os.path.exists(lockfile) and checks < 5:
            time.sleep(1)
            checks += 1

        with bb.tinfoil.Tinfoil(setup_logging=sl) as tinfoil:
            values = ()
            if target:
                tinfoil.prepare(quiet=2)
                d = tinfoil.parse_recipe(target)
                for var in vars:
                    values = values + (d.getVar(var, True) or 'None',)
            else:
                tinfoil.prepare(config_only=True, quiet=2)
                for var in vars:
                    values = values + (tinfoil.config_data.getVar(var, True) or 'None',)
            return values if len(values) > 1 else values[0]

    def create_tmp_layer(self):
        tmp_layer_dir = os.path.join(isar_root, 'meta-tmp')

        conf_dir = os.path.join(tmp_layer_dir, 'conf')
        os.makedirs(conf_dir, exist_ok=True)
        layer_conf_file = os.path.join(conf_dir, 'layer.conf')
        with open(layer_conf_file, 'w') as file:
            file.write('\
BBPATH .= ":${LAYERDIR}"\
\nBBFILES += "${LAYERDIR}/recipes-*/*/*.bbappend"\
\nBBFILE_COLLECTIONS += "tmp"\
\nBBFILE_PATTERN_tmp = "^${LAYERDIR}/"\
\nBBFILE_PRIORITY_tmp = "5"\
\nLAYERVERSION_tmp = "1"\
\nLAYERSERIES_COMPAT_tmp = "v0.6"\
')

        bblayersconf_file = os.path.join(self.build_dir, 'conf',
                                         'bblayers.conf')
        bb.utils.edit_bblayers_conf(bblayersconf_file, tmp_layer_dir, None)

        return tmp_layer_dir

    def cleanup_tmp_layer(self, tmp_layer_dir):
        bblayersconf_file = os.path.join(self.build_dir, 'conf',
                                         'bblayers.conf')
        bb.utils.edit_bblayers_conf(bblayersconf_file, None, tmp_layer_dir)
        bb.utils.prunedir(tmp_layer_dir)

    def get_tar_content(self, filename):
        try:
            tar = tarfile.open(filename)
            return tar.getnames()
        except Exception:
            return []

    def get_ssh_cmd_prefix(self, user, host, port, priv_key):
        cmd_prefix = 'ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no '\
                     '-p %s -o IdentityFile=%s %s@%s ' \
                     % (port, priv_key, user, host)

        return cmd_prefix


    def exec_cmd(self, cmd, cmd_prefix):
        proc = subprocess.run('exec ' + str(cmd_prefix) + ' "' + str(cmd) + '"', shell=True,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return proc.returncode, proc.stdout, proc.stderr


    def remote_send_file(self, src, dest, mode):
        priv_key = self.prepare_priv_key()
        cmd_prefix = self.get_ssh_cmd_prefix(self.ssh_user, self.ssh_host, self.ssh_port, priv_key)

        proc = subprocess.run('cat %s | %s install -m %s /dev/stdin %s' %
                              (src, cmd_prefix, mode, dest), shell=True,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return proc.returncode, proc.stdout, proc.stderr

    def run_script(self, script, cmd_prefix):
        script_dir = self.params.get('test_script_dir',
                                     default=os.path.abspath(os.path.dirname(__file__))) + '/scripts/'
        script_path = script_dir + script.split()[0]
        script_args = ' '.join(script.split()[1:])

        if not os.path.exists(script_path):
            self.log.error('Script not found: ' + script_path)
            return (2, '', 'Script not found: ' + script_path)

        rc, stdout, stderr = self.remote_send_file(script_path, "./ci.sh", "755")

        if rc != 0:
            self.log.error('Failed to deploy the script on target')
            return (rc, stdout, stderr)

        time.sleep(1)

        proc = subprocess.run('%s ./ci.sh %s' % (cmd_prefix, script_args), shell=True,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return (proc.returncode, proc.stdout, proc.stderr)

    def wait_connection(self, cmd_prefix, timeout):
        self.log.info('Waiting for SSH server ready...')

        rc = None
        stdout = ""
        stderr = ""

        goodcnt = 0
        # Use 3 good SSH ping attempts to consider SSH connection is stable
        while time.time() < timeout and goodcnt < 3:
            goodcnt += 1

            rc, stdout, stderr = self.exec_cmd('/bin/true', cmd_prefix)
            time.sleep(1)

            if rc != 0:
                goodcnt = 0

            time_left = timeout - time.time()
            self.log.info('SSH ping result: %d, left: %.fs' % (rc, time_left))

        return rc, stdout, stderr


    def prepare_priv_key(self):
        # copy private key to build directory (that is writable)
        priv_key = '%s/ci_priv_key' % self.build_dir
        if not os.path.exists(priv_key):
            shutil.copy(os.path.dirname(__file__) + '/keys/ssh/id_rsa', priv_key)
        os.chmod(priv_key, 0o400)

        return priv_key


    def remote_run(self, cmd=None, script=None, timeout=0):
        if cmd:
            self.log.info('Remote command is `%s`' % (cmd))
        if script:
            self.log.info('Remote script is `%s`' % (script))

        priv_key = self.prepare_priv_key()
        cmd_prefix = self.get_ssh_cmd_prefix(self.ssh_user, self.ssh_host, self.ssh_port, priv_key)

        rc = None
        stdout = ""
        stderr = ""

        if timeout != 0:
            rc, stdout, stderr = self.wait_connection(cmd_prefix, timeout)

        if rc == 0 or timeout == 0:
            if cmd is not None:
                rc, stdout, stderr = self.exec_cmd(cmd, cmd_prefix)
                self.log.info('`' + cmd + '` returned ' + str(rc))
            elif script is not None:
                rc, stdout, stderr = self.run_script(script, cmd_prefix)
                self.log.info('`' + script + '` returned ' + str(rc))

        return rc, stdout, stderr


    def ssh_start(self, user='ci', host='localhost', port=22,
                  cmd=None, script=None):
        self.log.info('===================================================')
        self.log.info('Running Isar SSH test for `%s@%s:%s`' % (user, host, port))
        self.log.info('Isar build folder is: ' + self.build_dir)
        self.log.info('===================================================')

        self.check_init()

        self.ssh_user = user
        self.ssh_host = host
        self.ssh_port = port

        priv_key = self.prepare_priv_key()
        cmd_prefix = self.get_ssh_cmd_prefix(self.ssh_user, self.ssh_host, self.ssh_port, priv_key)
        self.log.info('Connect command:\n' + cmd_prefix)

        if cmd is not None or script is not None:
            rc, stdout, stderr = self.remote_run(cmd, script)

            if rc != 0:
                self.fail('Failed with rc=%s' % rc)

            return stdout, stderr

        self.fail('No command to run specified')


    def vm_turn_on(self, arch='amd64', distro='buster', image='isar-image-base',
                   enforce_pcbios=False):
        logdir = '%s/vm_start' % self.build_dir
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        prefix = '%s-vm_start_%s_%s_' % (time.strftime('%Y%m%d-%H%M%S'),
                                         distro, arch)
        fd, boot_log = tempfile.mkstemp(suffix='_log.txt', prefix=prefix,
                                           dir=logdir, text=True)
        os.chmod(boot_log, 0o644)
        latest_link = '%s/vm_start_%s_%s_latest.txt' % (logdir, distro, arch)
        if os.path.exists(latest_link):
            os.unlink(latest_link)
        os.symlink(os.path.basename(boot_log), latest_link)

        cmdline = start_vm.format_qemu_cmdline(arch, self.build_dir, distro, image,
                                               boot_log, None, enforce_pcbios)
        cmdline.insert(1, '-nographic')

        self.log.info('QEMU boot line:\n' + ' '.join(cmdline))
        self.log.info('QEMU boot log:\n' + boot_log)

        p1 = subprocess.Popen('exec ' + ' '.join(cmdline), shell=True,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True)
        self.log.info("Started VM with pid %s" % (p1.pid))

        return p1, cmdline, boot_log


    def vm_wait_boot(self, p1, timeout):
        login_prompt = b' login:'

        poller = select.poll()
        poller.register(p1.stdout, select.POLLIN)
        poller.register(p1.stderr, select.POLLIN)

        while time.time() < timeout and p1.poll() is None:
            events = poller.poll(1000 * (timeout - time.time()))
            for fd, event in events:
                if event != select.POLLIN:
                    continue
                if fd == p1.stdout.fileno():
                    # Wait for the complete string if it is read in chunks
                    # like "i", "sar", " login:"
                    time.sleep(0.01)
                    data = os.read(fd, 1024)
                    if login_prompt in data:
                        self.log.info('Got login prompt')
                        return 0
                if fd == p1.stderr.fileno():
                    app_log.error(p1.stderr.readline().rstrip())

        self.log.error("Didn't get login prompt")
        return 1


    def vm_parse_output(self, boot_log, multiconfig, skip_modulecheck):
        # the printk of recipes-kernel/example-module
        module_output = b'Just an example'
        resize_output = None
        image_fstypes, \
        wks_file, \
        bbdistro = self.getVars('IMAGE_FSTYPES', \
                                'WKS_FILE', \
                                'DISTRO', \
                                target=multiconfig)

        # only the first type will be tested in start_vm.py
        if image_fstypes.split()[0] == 'wic':
            if wks_file:
                # ubuntu is less verbose so we do not see the message
                # /etc/sysctl.d/10-console-messages.conf
                if bbdistro and "ubuntu" not in bbdistro:
                    if "sdimage-efi-sd" in wks_file:
                        # output we see when expand-on-first-boot runs on ext4
                        resize_output = b'resized filesystem to'
                    if "sdimage-efi-btrfs" in wks_file:
                        resize_output = b': resize device '
        rc = 0
        if os.path.exists(boot_log) and os.path.getsize(boot_log) > 0:
            with open(boot_log, "rb") as f1:
                data = f1.read()
                if (module_output in data or skip_modulecheck):
                    if resize_output and not resize_output in data:
                        rc = 1
                        self.log.error("No resize output while expected")
                else:
                    rc = 2
                    self.log.error("No example module output while expected")
        return rc


    def vm_dump_dict(self, vm):
        f = open(self.vm_dict_file, "wb")
        pickle.dump(self.vm_dict, f)
        f.close()


    def vm_turn_off(self, vm):
        pid = self.vm_dict[vm][0]
        os.kill(pid, signal.SIGKILL)

        del(self.vm_dict[vm])
        self.vm_dump_dict(vm)

        self.log.info("Stopped VM with pid %s" % (pid))


    def vm_start(self, arch='amd64', distro='buster',
                 enforce_pcbios=False, skip_modulecheck=False,
                 image='isar-image-base', cmd=None, script=None,
                 keep=False):
        time_to_wait = self.params.get('time_to_wait', default=DEF_VM_TO_SEC)

        self.log.info('===================================================')
        self.log.info('Running Isar VM boot test for (' + distro + '-' + arch + ')')
        self.log.info('Remote command is ' + str(cmd))
        self.log.info('Remote script is ' + str(script))
        self.log.info('Isar build folder is: ' + self.build_dir)
        self.log.info('===================================================')

        self.check_init()

        timeout = time.time() + int(time_to_wait)

        vm = "%s_%s_%s_%d" % (arch, distro, image, enforce_pcbios)

        p1 = None
        pid = None
        cmdline = ""
        boot_log = ""

        run_qemu = True

        stdout = ""
        stderr = ""

        if vm in self.vm_dict:
            pid, cmdline, boot_log = self.vm_dict[vm]

            # Check that corresponding process exists
            proc = subprocess.run("ps -o cmd= %d" % (pid), shell=True, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if cmdline[0] in proc.stdout:
                self.log.info("Found '%s' process with pid '%d', use it" % (cmdline[0], pid))
                run_qemu = False

        if run_qemu:
            self.log.info("No qemu-system process for `%s` found, run new VM" % (vm))

            p1, cmdline, boot_log = self.vm_turn_on(arch, distro, image, enforce_pcbios)
            self.vm_dict[vm] = p1.pid, cmdline, boot_log
            self.vm_dump_dict(vm)

            rc = self.vm_wait_boot(p1, timeout)
            if rc != 0:
                self.vm_turn_off(vm)
                self.fail('Failed to boot qemu machine')

        if cmd is not None or script is not None:
            self.ssh_user='ci'
            self.ssh_host='localhost'
            self.ssh_port = 22
            for arg in cmdline:
                match = re.match(r".*hostfwd=tcp::(\d*).*", arg)
                if match:
                    self.ssh_port = match.group(1)
                    break

            priv_key = self.prepare_priv_key()
            cmd_prefix = self.get_ssh_cmd_prefix(self.ssh_user, self.ssh_host, self.ssh_port, priv_key)
            self.log.info('Connect command:\n' + cmd_prefix)

            rc, stdout, stderr = self.remote_run(cmd, script, timeout)
            if rc != 0:
                if not keep:
                    self.vm_turn_off(vm)
                self.fail('Failed to run test over ssh')
        else:
            multiconfig = 'mc:qemu' + arch + '-' + distro + ':' + image
            rc = self.vm_parse_output(boot_log, multiconfig, skip_modulecheck)
            if rc != 0:
                if not keep:
                    self.vm_turn_off(vm)
                self.fail('Failed to parse output')

        if not keep:
            self.vm_turn_off(vm)

        return stdout, stderr

    def get_config_tftp(self, yaml_name, machine, distro):
        with open(yaml_name, 'r', encoding='utf-8') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
        required_keys = [
            'tftp_server', 'nfs_server', 'tftp_root_path', 'nfs_root_path',
            'rpi_host', 'tty', 'switch_number', 'switch_port',
            'serial_number',
        ]
        output = subprocess.check_output(['bitbake', '-e',
            f'mc:{machine}-{distro}:isar-image-base'])
        bb_output = output.decode()
        rootfs_path = start_vm.get_bitbake_var(bb_output, 'IMAGE_ROOTFS') 
        for key in required_keys:
            if key not in yaml_data:
                self.error(f'{key} is required')
        config = tuple(yaml_data.get(key, None) for key in required_keys +
                ['username', 'ssh_port_tftp', 'ssh_port_nfs', 'ssh_port_rpi',
                 'ssh_key_path']) + (rootfs_path,)

        return config

    def get_config_sd(self, yaml_name, machine, distro):
        with open(yaml_name, 'r', encoding='utf-8') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
        required_keys = [
            'host', 'tty', 'switch_number', 'switch_port',
            'serial_number', 'sd_device_path',
        ]
        output = subprocess.check_output(['bitbake', '-e',
                                   f'mc:{machine}-{distro}:isar-image-base'])
        bb_output = output.decode()
        images_path = start_vm.get_bitbake_var(bb_output, 'DEPLOY_DIR_IMAGE')
        image_name = start_vm.get_bitbake_var(bb_output, 'SOURCE_IMAGE_FILE')
        for key in required_keys:
            if key not in yaml_data:
                self.error(f'{key} is required')
        config = tuple(yaml_data.get(key, None) for key in required_keys +
            ['ssh_port', 'username', 'ssh_key_path']) + (images_path,
                                                         image_name)

        return config

    def start_rpi_tftp(self, tftp_server, nfs_server, tftp_root_path,
                       nfs_root_path, rpi_host, tty, switch_number,
                       switch_port, serial_number, username,
                       ssh_port_tftp, ssh_port_nfs, ssh_port_rpi,
                       ssh_key_path, rootfs_path, distro, machine, model):

        current_ip = socket.gethostbyname(socket.gethostname())
        tftp_rpi_path = os.path.join(tftp_root_path, serial_number)
        nfs_rpi_path = os.path.join(nfs_root_path, 'isar-ci', serial_number,
                                    distro)
        fs_name = os.path.basename(rootfs_path.rstrip('/'))

        self.prepare_files_for_tftp(current_ip, tftp_server, tftp_rpi_path,
                                    nfs_server, nfs_rpi_path, fs_name,
                                    rootfs_path, tftp_root_path, model,
                                    username, ssh_port_tftp, ssh_key_path)

        self.prepare_files_for_nfs(current_ip, nfs_server, nfs_rpi_path,
                                   fs_name, rootfs_path, username,
                                   ssh_port_nfs, ssh_key_path)

        self.boot_board(current_ip, rpi_host, tty, serial_number,
                        switch_number, switch_port, ssh_port_rpi, username,
                        ssh_key_path, distro, machine)

    def start_board_muxer(self, host, tty, switch_number, switch_port,
                          serial_number, sd_device_path, ssh_port, username,
                          ssh_key_path, images_path, image_name, machine,
                          distro):
        current_ip = socket.gethostbyname(socket.gethostname())
        self.flash_board(current_ip, host, ssh_port, username,
                         ssh_key_path, images_path, image_name,
                         sd_device_path, distro, machine)
        self.boot_board(current_ip, host, tty, serial_number, switch_number,
                        switch_port, ssh_port, username, ssh_key_path,
                        distro, machine)

    def configure_firmware_files(self, current_ip, tftp_server,
                                 ssh_port_tftp, username, ssh_key_path,
                                 bootcode_rpi_path, tftp_rpi_path,
                                 nfs_server, nfs_rpi_path, fs_name, model):
        if current_ip != tftp_server:
            with ssh.Session(tftp_server, ssh_port_tftp, username,
                             ssh_key_path) as session:
                if model in ['3b', '3b+']:
                    session.cmd(
                        f'sed -i -e "s/BOOT_UART=0/BOOT_UART=1/" '
                        f'{bootcode_rpi_path}', ignore_status=False
                )
                session.cmd(
                    f'echo "[all]\n'
                    f'enable_uart=1" > {tftp_rpi_path}/config.txt',
                    ignore_status=False
                )
                session.cmd(
                    f'echo "dwc_otg.lpm_enable=0 console=serial0,'
                    f'115200 console=tty1 root=/dev/nfs nfsroot={nfs_server}'
                    f':{nfs_rpi_path}/{fs_name}/,vers=4.1,proto=tcp rw '
                    f'ip=dhcp rootwait" > {tftp_rpi_path}/cmdline.txt',
                    ignore_status=False
                )
                session.quit()

        elif current_ip == tftp_server:
            if model in ['3b', '3b+']:
                with open(bootcode_rpi_path, 'r+b') as bootcode_file:
                    bootcode_data = bootcode_file.read()
                    bootcode_data = bootcode_data.replace(b'BOOT_UART=0',
                                                          b'BOOT_UART=1')
                    bootcode_file.seek(0)
                    bootcode_file.write(bootcode_data)
                    bootcode_file.truncate()
            config_path = os.path.join(tftp_rpi_path, 'config.txt')
            with open(config_path, 'w', encoding='utf-8') as config_file:
                config_file.write('[all]\nenable_uart=1')
            cmdline_path = os.path.join(tftp_rpi_path, 'cmdline.txt')
            with open(cmdline_path, 'w', encoding='utf-8') as cmdline_file:
                cmdline_file.write(
                    f'dwc_otg.lpm_enable=0 console=serial0,115200 '
                    f'console=tty1 root=/dev/nfs nfsroot={nfs_server}:'
                    f'{nfs_rpi_path}/{fs_name},vers=4.1,proto=tcp rw '
                    f'ip=dhcp rootwait'
                )

    def prepare_files_for_tftp(self, current_ip, tftp_server, tftp_rpi_path,
                               nfs_server, nfs_rpi_path, fs_name,
                               rootfs_path, tftp_root_path, model, username,
                               ssh_port_tftp, ssh_key_path):

        boot_files = ['cmdline.txt', 'config.txt', 'kernel8.img']
        bootcode_rpi_path = None

        if model in ['2b', '3b', '3b+']:
            boot_files.extend(['fixup.dat', 'start.elf'])
            bootcode_rpi_path = os.path.join(tftp_root_path, 'bootcode.bin')
            bootcode_orig_path = os.path.join(rootfs_path, 'boot',
                                              'bootcode.bin')
            if model == '2b':
                boot_files.append('bcm2710-rpi-2-b.dtb')
            elif model == '3b':
                boot_files.append('bcm2710-rpi-3-b.dtb')
            elif model == '3b+':
                boot_files.append('bcm2710-rpi-3-b-plus.dtb')
        elif model == '4b':
            boot_files.extend(['bcm2711-rpi-4-b.dtb', 'fixup4.dat',
                               'start4.elf'])

        if current_ip != tftp_server:
            with ssh.Session(tftp_server, ssh_port_tftp, username,
                             ssh_key_path) as session:
                session.cmd(f'mkdir -p {tftp_rpi_path}')
            if model in ['2b', '3b', '3b+']:
                process.run(
                    f'rsync -az -e "ssh -p {ssh_port_tftp} -i {ssh_key_path}"'
                    f' {bootcode_orig_path} {username}@{tftp_server}:'
                    f'{tftp_root_path}/'
                )
            for file in boot_files:
                build_boot_path = os.path.join(rootfs_path, 'boot', file)
                process.run(
                    f'rsync -az -e "ssh -p {ssh_port_tftp} -i {ssh_key_path}"'
                    f' {build_boot_path} {username}@{tftp_server}:'
                    f'{tftp_rpi_path}/'
                )

        elif current_ip == tftp_server:
            os.makedirs(tftp_rpi_path, exist_ok=True)
            for file in boot_files:
                build_boot_path = os.path.join(rootfs_path, 'boot', file)
                shutil.copy(build_boot_path, tftp_rpi_path)
            if model in ['2b', '3b', '3b+']:
                shutil.copy(bootcode_orig_path, tftp_root_path)

        self.configure_firmware_files(
            current_ip, tftp_server, ssh_port_tftp, username, ssh_key_path,
            bootcode_rpi_path, tftp_rpi_path, nfs_server, nfs_rpi_path,
            fs_name, model
        )

    def prepare_files_for_nfs(self, current_ip, nfs_server, nfs_rpi_path,
                              fs_name, rootfs_path, username,
                              ssh_port_nfs, ssh_key_path):

        archive_name = f'{fs_name}.tar.gz'
        if current_ip != nfs_server:
            with ssh.Session(nfs_server, ssh_port_nfs, username,
                             ssh_key_path) as session:
                session.cmd(f'mkdir -p {nfs_rpi_path}')
            os.chdir(f'{rootfs_path}/..')
            process.run(f'tar -czf {archive_name} {fs_name}', sudo=True)
            process.run(
                f'rsync -az -e "ssh -p {ssh_port_nfs} -i {ssh_key_path}" '
                f'{archive_name} {username}@{nfs_server}:{nfs_rpi_path}'
            )
            process.run(f'rm -f {archive_name}', sudo=True)
            with ssh.Session(nfs_server, ssh_port_nfs, username,
                             ssh_key_path) as session:
                session.cmd(
                    f'cd {nfs_rpi_path} && '
                    f'sudo tar -xzf {archive_name} && '
                    f'sudo rm -f {nfs_rpi_path}/{archive_name}',
                    ignore_status=False
                )
            session.quit()

        elif current_ip == nfs_server:
            os.makedirs(nfs_rpi_path, exist_ok=True)
            os.chdir(f'{rootfs_path}/..')
            process.run(
                f'tar -czf {nfs_rpi_path}/{archive_name} {fs_name}',
                sudo=True
            )
            os.chdir(nfs_rpi_path)
            process.run(f'tar -xzf {archive_name}', sudo=True)
            process.run(f'rm -f {nfs_rpi_path}/{archive_name}',
                        sudo=True)

    def flash_board(self, current_ip, host, ssh_port, username,
                    ssh_key_path, images_path, image_name, sd_device_path,
                    distro, machine):
        board_dir = f'/home/{username}/{machine}'
        if current_ip != host:
            with ssh.Session(host, ssh_port, username,
                             ssh_key_path) as session:
                session.cmd(f'mkdir -p {board_dir}')
            process.run(
                f'scp -P {ssh_port} -i {ssh_key_path} {images_path}/'
                f'{image_name} {username}@{host}:{board_dir}'
            )
            with ssh.Session(host, ssh_port, username, ssh_key_path) \
                as session:
                session.cmd(
                    f'cd {board_dir} && '
                    f'sudo sd-mux-ctrl --device-serial=sd-wire_1 --ts && '
                    f'bmaptool create {image_name} > '
                    f'{machine}-{distro}-isar-ci.bmap && sudo '
                    f'bmaptool copy --bmap {machine}-{distro}-isar-ci.bmap '
                    f'{image_name} {sd_device_path} && '
                    f'sudo sd-mux-ctrl --device-serial=sd-wire_1 --dut',
                    ignore_status=False
                )
            session.quit()

        elif current_ip == host:
            os.makedirs(board_dir, exist_ok=True)
            shutil.copy(images_path, board_dir)
            os.chdir(board_dir)
            process.run(
                'sd-mux-ctrl --device-serial=sd-wire_1 --ts', sudo=True)
            process.run(
                f'bmaptool create {image_name} > '
                f'{machine}-{distro}-isar-ci.bmap')
            process.run(
                f'bmaptool copy --bmap {machine}-{distro}-isar-ci.bmap '
                f'{image_name} {sd_device_path}', sudo=True)
            process.run(
                'sd-mux-ctrl --device-serial=sd-wire_1 --dut', sudo=True)

    def save_logs(self, distro, serial_number):
        logdir = f'{self.build_dir}/hw_start'
        os.makedirs(logdir, exist_ok=True)
        prefix = f"{time.strftime('%Y%m%d-%H%M%S')}\
-hw_start_{distro}_{serial_number}_"
        fd, boot_log = tempfile.mkstemp(suffix='_log.txt', prefix=prefix,
                                        dir=logdir, text=True)
        os.chmod(boot_log, 0o644)
        latest_link = f'{logdir}/hw_start_{distro}_{serial_number}_latest.txt'
        if os.path.exists(latest_link):
            os.unlink(latest_link)
        os.symlink(os.path.basename(boot_log), latest_link)
        return boot_log

    def setup_serial_and_turn_on(self, current_ip, host, ssh_port, username,
                                 ssh_key_path, tty, switch_number,
                                 switch_port, machine):
        self.log.info('=====================================================')
        self.log.info('         Running Isar hardware boot test ...         ')
        self.log.info('=====================================================')

        if current_ip == host:
            with open(
                'kerm-{machine}', 'w', encoding='utf-8') as kerm_file:
                kerm_file.write(
                    f'set line {tty}\n'
                    f'set speed 115200\n'
                    f'set carrier-watch off\n'
                    f'set flow-control none\n'
                    f'connect'
                )
            process.run(
                f'sudo clewarecontrol -d {switch_number} -c 1 '
                f'-as {switch_port} 0'
            )
            time.sleep(5)
            process.run(
                f'sudo clewarecontrol -d {switch_number} -c 1 '
                f'-as {switch_port} 1'
            )
        elif current_ip != host:
            with ssh.Session(host, ssh_port, username, ssh_key_path) \
                as session:
                session.cmd(
                    f'echo "set line {tty}\n'
                    f'set speed 115200\n'
                    f'set carrier-watch off\n'
                    f'set flow-control none\n'
                    f'connect" > kerm-{machine}', ignore_status=False
                )
                session.cmd(
                    f'sudo clewarecontrol -d {switch_number} -c 1 '
                    f'-as {switch_port} 0', ignore_status=False
                )
                time.sleep(5)
                session.cmd(
                    f'sudo clewarecontrol -d {switch_number} -c 1 '
                    f'-as {switch_port} 1', ignore_status=False
                )

    def boot_board(self, current_ip, host, tty, serial_number,
                   switch_number, switch_port, ssh_port, username,
                   ssh_key_path, distro, machine):

        boot_log = self.save_logs(distro, serial_number)
        self.setup_serial_and_turn_on(
            current_ip, host, ssh_port, username, ssh_key_path, tty,
            switch_number, switch_port, machine
        )

        cmdline = f'kermit -y kerm-{machine}'
        timeout = time.time() + 60
        output = ''
        if current_ip == host:
            p1 = subprocess.Popen(
                'exec ' + ' '.join(cmdline), shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, universal_newlines=True
            )
            rc = self.vm_wait_boot(p1, timeout)
            process.run(
                f'sudo clewarecontrol -d {switch_number} -c 1 '
                f'-as {switch_port} 0'
            )
            if rc != 0:
                self.fail('Failed to boot the board')

        elif current_ip != host:
            login_prompt = 'isar login:'
            ssh_board = paramiko.SSHClient()
            ssh_board.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_board.connect(hostname=host, port=ssh_port,
                              username=username, key_filename=ssh_key_path)
            stdin, stdout, stderr = ssh_board.exec_command(cmdline,
                                                           get_pty=True)
            while time.time() < timeout:
                data = stdout.channel.recv(4096).decode('utf-8', 'ignore')
                output += data
                if login_prompt in data:
                    self.log.info('Got login prompt')
                    ssh_board.exec_command(
                        f'sudo clewarecontrol -d {switch_number} -c 1 '
                        f'-as {switch_port} 0'
                    )
                    with open(boot_log, 'w', encoding='utf-8') as log_file:
                        log_file.write(output)
                    ssh_board.close()
                    return 0
                time.sleep(0.2)
            with open(boot_log, 'w', encoding='utf-8') as log_file:
                log_file.write(output)
            self.log.info("Didn't get login prompt")
            ssh_board.exec_command(
                f'sudo clewarecontrol -d {switch_number} -c 1 '
                f'-as {switch_port} 0'
            )
            ssh_board.close()
            self.fail('Failed to boot the board')
