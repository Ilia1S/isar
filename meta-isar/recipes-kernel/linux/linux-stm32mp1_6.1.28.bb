# This software is a part of Isar.
# Copyright (C) 2024 ilbers GmbH

require recipes-kernel/linux/linux-custom.inc

SRC_URI += "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${PV}.tar.xz \
    file://ftpm-module.cfg \
    file://fragment-01-multiv7_cleanup.cfg \
    file://fragment-02-multiv7_addons.cfg \
    file://0003-ARM-dts-stm32-remove-stm32mp157-scmi.dtb-from-compil.patch \
    file://0004-ARM-dts-stm32-include-board-scmi.dtsi-in-each-board-.patch \
    file://0005-ARM-stm32-add-STM32MP151-and-STM32MP153-SoC-support.patch \
    file://0006-ARM-dts-stm32-fullfill-diversity-with-OPP-for-STM32M.patch \
    file://0009-ARM-dts-stm32-adapt-stm32mp157a-dk1-board-to-stm32-D.patch \
    file://0010-ARM-dts-stm32-add-stm32mp157f-dk2-board-support.patch \
    file://0011-ARM-dts-stm32-add-stm32mp157d-dk1-board-support.patch"

SRC_URI[sha256sum] = "7a094c1428b20fef0b5429e4effcc6ed962a674ac6f04e606d63be1ddcc3a6f0"

S = "${WORKDIR}/linux-${PV}"

KBUILD_DEPENDS:append = "lzop, u-boot-tools"

KERNEL_DEFCONFIG = "multi_v7_defconfig"

LINUX_VERSION_EXTENSION = "-isar"

KERNEL_EXTRA_BUILDARGS = "LOADADDR=0xC2000040"

COMPATIBLE_MACHINE = "stm32mp15x"
