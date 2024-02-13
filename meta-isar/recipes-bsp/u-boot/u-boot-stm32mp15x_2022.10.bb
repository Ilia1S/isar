#
# Copyright (C) Siemens AG, 2020
# Copyright (C) 2024 ilbers GmbH
#
# SPDX-License-Identifier: MIT

require recipes-bsp/u-boot/u-boot-custom.inc

SRC_URI += " https://ftp.denx.de/pub/u-boot/u-boot-${PV}.tar.bz2 \
    file://0003-drivers-tee-optee-remove-unused-probe-local-variable.patch \
    file://0004-drivers-tee-optee-discover-OP-TEE-services.patch \
    file://0005-drivers-rng-optee_rng-register-to-CONFIG_OPTEE_SERVI.patch \
    file://0010-stm32mp-stm32prog-support-empty-flashlayout.patch \
    file://0011-stm32mp-stm32prog-change-default-flashlayout-locatio.patch \
    file://0012-stm32mp-stm32prog-solve-warning-for-64bits-compilati.patch \
    file://0013-stm32mp-stm32prog-correctly-handle-OTP-when-SMC-is-n.patch \
    file://0014-ARM-dts-stm32mp-alignment-with-v6.0-rc3.patch \
    file://0015-stm32mp-stm32prog-improve-the-partitioning-trace.patch \
    file://0016-board-st-stm32mp1-use-of-correct-compatible-string-t.patch \
    file://0017-arm-stm32mp-add-defines-for-BSEC_LOCK-status-in-stm3.patch \
    file://0018-arm-stm32mp-introduced-read_close_status-function-in.patch \
    file://0019-arm-stm32mp-support-several-key-in-command-stm32key.patch \
    file://0020-arm-stm32mp-adapt-the-command-stm32key-for-STM32MP13.patch \
    file://0021-configs-stm32mp1-cleanup-config-file.patch \
    file://0022-ARM-dts-stm32mp15-update-DDR-node.patch \
    file://0023-ARM-dts-stm32-DT-sync-with-kernel-v6.0-rc4-for-MCU-s.patch \
    file://0031-configs-increase-SYS_MALLOC_F_LEN-for-STM32-MCU-s-bo.patch \
    file://0032-phy-Add-generic_-setup-shutdown-_phy-helpers.patch \
    file://0033-usb-ohci-Make-usage-of-generic_-setup-shutdown-_phy-.patch \
    file://0034-usb-ehci-Make-usage-of-generic_-setup-shutdown-_phy-.patch \
    file://0035-usb-ehci-Remove-unused-ehci_-setup-shutdown-_phy-hel.patch \
    file://0036-firmware-scmi-fix-the-multi-channel-support-with-CCF.patch \
    file://0037-ARM-dts-stm32-Remove-buck3-regulator-always-on-on-AV.patch \
    file://0038-ARM-stm32-Enable-btrfs-support-on-DHSOM.patch \
    file://0039-ARM-dts-stm32-Drop-extra-newline-from-AV96-U-Boot-ex.patch \
    file://0040-ARM-dts-stm32-Add-DHCOR-based-Testbench-board.patch \
    file://0041-ARM-dts-stm32-Fix-and-expand-PLL-configuration-comme.patch \
    file://0042-ARM-dts-stm32-update-SCMI-dedicated-file.patch \
    file://0044-mmc-stm32_sdmmc2-add-dual-data-rate-support.patch \
    file://0045-mmc-stm32_sdmmc2-protect-against-unsupported-modes.patch \
    file://0046-mmc-stm32_sdmmc2-manage-vqmmc.patch \
    file://0047-clk-update-clk_clean_rate_cache-to-use-private-clk-s.patch \
    file://0048-dt-bindings-stm32mp13-add-clock-reset-support-for-ST.patch \
    file://0049-clk-stm32mp13-introduce-STM32MP13-RCC-driver.patch \
    file://0050-arm-dts-stm32mp13-add-support-of-RCC-driver.patch \
    file://0051-adc-stm32mp15-split-channel-init-into-several-routin.patch \
    file://0052-adc-stm32mp15-add-support-of-generic-channels-bindin.patch \
    file://0053-ARM-dts-stm32-add-sdmmc-cd-gpios-for-STM32MP135F-DK.patch \
    file://0054-ARM-dts-stm32-Drop-MMCI-interrupt-names.patch \
    file://0055-ARM-stm32-Add-boot-counter-to-DHSOM.patch \
    file://0056-ARM-stm32-Add-version-variable-to-DHSOM.patch \
    file://0057-ARM-stm32-Enable-assorted-ST-specific-commands-on-DH.patch \
    file://0058-ARM-stm32-Increment-boot-counter-in-SPL-on-DHSOM.patch \
    file://0059-ARM-stm32-Increment-WDT-by-default-on-DHSOM.patch \
    file://0060-dfu-Make-DFU-virtual-backend-SPL-friendly.patch \
    file://0061-firmware-scmi-use-protocol-node-name-to-bind-the-scm.patch \
    file://0062-phy-usbphyc-use-regulator_set_enable_if_allowed-for-.patch \
    file://0063-dm-pmic-ignore-disabled-node-in-pmic_bind_children.patch \
    file://0064-cmd-pxe_utils-Limit-fdtcontroladdr-usage-to-non-fitI.patch \
    file://0065-cmd-pxe-reorder-kernel-treatment-in-label_boot.patch \
    file://0066-cmd-pxe-support-INITRD-and-FDT-selection-with-FIT.patch \
    file://0067-cmd-pxe-use-strdup-to-copy-config.patch \
    file://0068-tpm2-ftpm-open-session-with-privileged-ree-login.patch \
    file://0069-tee-optee-don-t-fail-probe-because-of-optee-rng.patch \
    file://0070-tee-optee-discover-services-dependent-on-tee-supplic.patch \
    file://0071-optee-bind-the-TA-drivers-on-OP-TEE-node.patch \
    file://0072-cmd-mtdparts-add-SYS_MTDPARTS_RUNTIME-dependency-on-.patch \
    file://0073-env-ubi-add-support-of-command-env-erase.patch \
    file://0074-env-add-failing-trace-in-env_erase.patch \
    file://0075-gpio-Get-rid-of-gpio_hog_probe_all.patch \
    file://0076-ARM-dts-stm32-update-vbus-supply-of-usbphyc_port0-on.patch \
    file://0077-usb-onboard-hub-add-driver-to-manage-onboard-hub-sup.patch \
    file://0078-configs-stm32-enable-USB-onboard-HUB-driver.patch \
    file://0079-ARM-dts-stm32-add-support-for-USB2514B-onboard-hub-o.patch \
    file://0080-adc-stm32mp15-add-calibration-support.patch \
    file://0081-ARM-dts-stm32mp15-remove-clksrc-include-in-SCMI-dtsi.patch \
    file://0082-ARM-dts-stm32mp15-fix-typo-in-stm32mp15xx-dkx.dtsi.patch \
    file://0083-ARM-dts-stm32-Add-timer-interrupts-on-stm32mp15.patch \
    file://0084-stm32mp-cosmetic-Update-of-bsec-driver.patch \
    file://0085-stm32mp-Add-OP-TEE-support-in-bsec-driver.patch \
    file://0086-stm32mp-Add-support-of-STM32MP13x-in-bsec-driver.patch \
    file://0087-configs-stm32mp13-Activate-CONFIG_CMD_FUSE.patch \
    file://0088-board-st-Add-support-of-STM32MP13x-boards-in-stm32bo.patch \
    file://0089-configs-stm32mp13-Activate-command-stm32key.patch \
    file://0090-usb-hub-allow-to-increase-HUB_DEBOUNCE_TIMEOUT.patch \
    file://0091-tee-optee-fix-a-print-error-on-rng-probing.patch \
    file://0092-tee-optee-fix-uuid-comparisons-on-service-discovery.patch \
    file://0095-cmd-clk-probe-the-clock-before-dump-them.patch \
    file://0096-arm-Rename-STM32MP13x.patch \
    file://0097-arm-Rename-STM32MP15x.patch \
    file://0098-Makefile-link-with-no-warn-rwx-segments.patch \
    file://0099-image-Correct-strncpy-warning-with-image_set_name.patch \
    file://0100-Makefile-Link-with-z-noexectack.patch \
    file://0101-libfdt-Fix-invalid-version-warning.patch \
    file://0102-libfdt-Fix-build-with-python-3.10.patch \
    file://0103-fdt-Move-to-setuptools.patch \
    file://0104-pylibfdt-Fix-version-normalization-warning.patch \
    file://0105-pylibfdt-Fix-disable-version-normalization.patch \
    file://0106-pylibfdt-Allow-version-normalization-to-fail.patch \
    file://0107-ARM-dts-stm32-fix-node-name-order-and-node-name-and-.patch \
    file://0108-ARM-dts-stm32-reordering-nodes-in-stm32mp151.dtsi-fi.patch \
    file://0110-configs-Resync-with-savedefconfig.patch \
    file://0111-ARM-dts-stm32-remove-stm32mp157-scmi.dtb-from-compil.patch \
    file://0112-ARM-dts-stm32-include-board-scmi.dtsi-in-each-board-.patch \
    file://0113-ARM-dts-stm32-fullfill-diversity-with-OPP-for-STM32M.patch \
    file://0114-ARM-dts-stm32-adapt-stm32mp157a-dk1-board-to-stm32-D.patch \
    file://0115-ARM-dts-stm32-add-stm32mp157f-dk2-board-support.patch \
    file://0116-board-st-stm32mp1-add-stm32mp157f-dk2-support.patch \
    file://0117-ARM-dts-stm32-add-stm32mp157d-dk1-board-support.patch"

SRC_URI[sha256sum] = "50b4482a505bc281ba8470c399a3c26e145e29b23500bc35c50debd7fa46bdf8"

DEBIAN_BUILD_DEPENDS += ", swig, python3-setuptools, python3-dev:native, \
    libssl-dev:native, libssl-dev:armhf"

S = "${WORKDIR}/u-boot-${PV}"

U_BOOT_EXTRA_BUILDARGS = "DEVICE_TREE=stm32mp157d-dk1"

COMPATIBLE_MACHINE = "stm32mp15x"
