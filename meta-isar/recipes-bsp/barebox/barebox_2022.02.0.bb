# This software is a part of Isar.
# Copyright (C) 2022-2024 ilbers GmbH

inherit dpkg

require recipes-bsp/barebox/barebox.inc

SRC_URI += "https://git.pengutronix.de/cgit/barebox/snapshot/barebox-${PV}.tar.gz \
    file://0001-ARM-fix-GCC-11.x-build-failures-for-ARMv7.patch \
    file://0001-of_dump-Add-a-simple-node-check-up.patch"

S = "${WORKDIR}/barebox-${PV}"

SRC_URI[sha256sum] = "01fb3799840bde34014981557361dcae1db23764708bb7b151ec044eb022fbe8"

BAREBOX_VERSION_EXTENSION = "-isar"
