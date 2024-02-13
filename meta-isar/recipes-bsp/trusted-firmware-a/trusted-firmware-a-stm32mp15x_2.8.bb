#
# Copyright (C) Siemens AG, 2020
# Copyright (C) 2024 ilbers GmbH
#
# SPDX-License-Identifier: MIT

require recipes-bsp/trusted-firmware-a/trusted-firmware-a-custom.inc

SRC_URI += "https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git/snapshot/trusted-firmware-a-${PV}.tar.gz \
    file://0001-feat-stm32mp15-fdts-add-stm32mp157d-dk1-board.patch \
    file://0001-feat-stm32mp15-fdts-fulfill-diversity-for-STM32M15x-.patch"
SRC_URI[sha256sum] = "df4e0f3803479df0ea4cbf3330b59731bc2efc2112c951f9adb3685229163af9"

S = "${WORKDIR}/trusted-firmware-a-${PV}"

DEPENDS = "u-boot-${MACHINE} optee-os-${MACHINE}"

DEBIAN_BUILD_DEPENDS += ", optee-os-${MACHINE}, u-boot-${MACHINE}, \
    device-tree-compiler, git, libssl-dev:native"

TF_A_PLATFORM = "stm32mp1"

TF_A_EXTRA_BUILDARGS = " \
    ARCH=aarch32 ARM_ARCH_MAJOR=7 AARCH32_SP=optee \
    STM32MP_SDMMC=1 DTB_FILE_NAME=stm32mp157d-dk1.dtb \
    BL32=/usr/lib/optee-os/${MACHINE}/tee-header_v2.bin \
    BL32_EXTRA1=/usr/lib/optee-os/${MACHINE}/tee-pager_v2.bin \
    BL32_EXTRA2=/usr/lib/optee-os/${MACHINE}/tee-pageable_v2.bin \
    BL33=/usr/lib/u-boot/${MACHINE}/u-boot-nodtb.bin \
    BL33_CFG=/usr/lib/u-boot/${MACHINE}/u-boot.dtb \
    FW_CONFIG=fdts/stm32mp157d-dk1-fw-config.dts all fip"

TF_A_BINARIES = "release/tf-a-stm32mp157d-dk1.stm32 release/fip.bin"

COMPATIBLE_MACHINE = "stm32mp15x"
