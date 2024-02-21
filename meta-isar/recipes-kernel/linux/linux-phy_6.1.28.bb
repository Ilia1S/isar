# This software is a part of Isar.
# Copyright (C) 2024 ilbers GmbH

require recipes-kernel/linux/linux-custom.inc

SRC_URI += "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${PV}.tar.xz"

SRC_URI[sha256sum] = "7a094c1428b20fef0b5429e4effcc6ed962a674ac6f04e606d63be1ddcc3a6f0"

S = "${WORKDIR}/linux-${PV}"

KBUILD_DEPENDS:append = "lzop"

KERNEL_DEFCONFIG = "imx_v6_v7_defconfig"

LINUX_VERSION_EXTENSION = "-isar"

KERNEL_EXTRA_BUILDARGS = "all imx6q-phytec-mira-rdk-nand.dtb"

COMPATIBLE_MACHINE = "phyboard-mira"
