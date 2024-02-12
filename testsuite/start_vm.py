#!/usr/bin/env python3
#
# Helper script to start QEMU with Isar image
# Copyright (c) 2019-2014, ilbers GmbH

import os
import socket
import subprocess

def get_bitbake_env(arch, distro, image):
    multiconfig = 'mc:qemu' + arch + '-' + distro + ':' + image
    output = subprocess.check_output(['bitbake', '-e', str(multiconfig)])
    return output

def get_bitbake_var(output, var):
    ret = ''
    for line in output.splitlines():
        if line.startswith(var + '='):
            ret = line.split('"')[1]
    return ret

def format_qemu_cmdline(arch, build, distro, image, out, pid,
                        enforce_pcbios=False, secureboot=False):
    bb_output = get_bitbake_env(arch, distro, image).decode()

    extra_args = ''

    image_type = get_bitbake_var(bb_output, 'IMAGE_FSTYPES').split()[0]
    deploy_dir_image = get_bitbake_var(bb_output, 'DEPLOY_DIR_IMAGE')
    base = 'ubuntu' if distro in ['jammy', 'focal'] else 'debian'

    rootfs_image = \
        image + '-' + base + '-' + distro + '-qemu' + machine + arch + '.' + image_type

    if image_type == 'ext4':
        kernel_image = deploy_dir_image + '/' + get_bitbake_var(bb_output, 'KERNEL_IMAGE')
        initrd_image = get_bitbake_var(bb_output, 'INITRD_DEPLOY_FILE')

        if not initrd_image:
            initrd_image = '/dev/null'
        else:
            initrd_image = deploy_dir_image + '/' + initrd_image

        serial = get_bitbake_var(bb_output, 'MACHINE_SERIAL')
        root_dev = get_bitbake_var(bb_output, 'QEMU_ROOTFS_DEV')
        kargs = ['-append', '"console=' + serial + ' root=/dev/' + root_dev + ' rw"']

        extra_args = ['-kernel', kernel_image, '-initrd', initrd_image]
        extra_args.extend(kargs)
    elif image_type == 'wic':
        extra_args = ['-snapshot']
    else:
        raise ValueError('Invalid image type: ' + str(image_type))

    qemu_arch = get_bitbake_var(bb_output, 'QEMU_ARCH')
    qemu_machine = get_bitbake_var(bb_output, 'QEMU_MACHINE')
    qemu_cpu = get_bitbake_var(bb_output, 'QEMU_CPU')
    qemu_disk_args = get_bitbake_var(bb_output, 'QEMU_DISK_ARGS')

    if out:
        extra_args.extend(['-chardev','stdio,id=ch0,logfile=' + out])
        extra_args.extend(['-serial','chardev:ch0'])
        extra_args.extend(['-monitor','none'])
    if pid:
        extra_args.extend(['-pidfile', pid])

    qemu_disk_args = qemu_disk_args.replace('##ROOTFS_IMAGE##', deploy_dir_image + '/' + rootfs_image).split()

    if secureboot:
        qemu_disk_args.extend(['-drive', 'if=pflash,format=raw,unit=1,file="/usr/share/OVMF/OVMF_VARS_4M.ms.fd"'])

    if enforce_pcbios and '-bios' in qemu_disk_args:
        bios_idx = qemu_disk_args.index('-bios')
        del qemu_disk_args[bios_idx : bios_idx+2]

    # Support SSH access from host
    ssh_sock = socket.socket()
    ssh_sock.bind(('', 0))
    ssh_port=ssh_sock.getsockname()[1]
    extra_args.extend(['-device', 'e1000,netdev=net0'])
    extra_args.extend(['-netdev', 'user,id=net0,hostfwd=tcp::' + str(ssh_port) + '-:22'])

    cmd = ['qemu-system-' + qemu_arch, '-m', '1024M']

    if qemu_machine:
        cmd.extend(['-M', qemu_machine])

    if qemu_cpu:
        cmd.extend(['-cpu', qemu_cpu])

    cmd.extend(extra_args)
    cmd.extend(qemu_disk_args)

    return cmd

def start_qemu(arch, build, distro, image, out, pid, enforce_pcbios,
               secureboot):
    cmdline = format_qemu_cmdline(arch, build, distro, image, out, pid,
                                  enforce_pcbios, secureboot)
    cmdline.insert(1, '-nographic')
    print(cmdline)
    p1 = subprocess.call('exec ' + ' '.join(cmdline), shell=True)
