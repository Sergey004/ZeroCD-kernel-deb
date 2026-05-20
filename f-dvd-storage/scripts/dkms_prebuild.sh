#!/usr/bin/env bash
# scripts/dkms_prebuild.sh
#
# Вызывается DKMS перед сборкой. Переменные окружения от DKMS:
#   kernel_source_dir  — /lib/modules/<ver>/build  (или полный source tree)
#   kernelver          — версия ядра
#   arch               — arm64
#   dkms_tree          — /var/lib/dkms
#   PACKAGE_NAME       — f-dvd-storage
#   PACKAGE_VERSION    — 1.0.0
#
set -euo pipefail

# DKMS копирует source tree в build директорию перед вызовом PRE_BUILD.
# BUILD_DIR — это место где мы находимся во время сборки.
BUILD_DIR="${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build"
SRC_DIR="${BUILD_DIR}/src"

log()  { echo "[f-dvd-storage prebuild] $*"; }
fail() { echo "[f-dvd-storage prebuild] ERROR: $*" >&2; exit 1; }

log "kernelver        = ${kernelver:-unknown}"
log "kernel_source_dir= ${kernel_source_dir}"
log "BUILD_DIR        = ${BUILD_DIR}"

# ── Найти f_mass_storage.c ──────────────────────────────────────────────────
GADGET_DIR=""
for d in \
    "${kernel_source_dir}/drivers/usb/gadget/function" \
    "/usr/src/linux-headers-${kernelver}/drivers/usb/gadget/function" \
    "/usr/src/linux-source-${kernelver%%-*}/drivers/usb/gadget/function"
do
    if [ -f "${d}/f_mass_storage.c" ]; then
        GADGET_DIR="${d}"
        break
    fi
done

[ -z "$GADGET_DIR" ] && fail "f_mass_storage.c не найден.
Установи: sudo apt install raspberrypi-kernel-headers
  или:    sudo apt install linux-headers-${kernelver}"

log "Источник: ${GADGET_DIR}"

# ── Копируем файлы ──────────────────────────────────────────────────────────
mkdir -p "${SRC_DIR}"
log "Копируем storage_common.{c,h} и f_mass_storage.c ..."
cp "${GADGET_DIR}/storage_common.c" "${SRC_DIR}/storage_dvd_common.c"
cp "${GADGET_DIR}/storage_common.h" "${SRC_DIR}/storage_dvd_common.h"
cp "${GADGET_DIR}/f_mass_storage.c" "${SRC_DIR}/f_dvd_storage_base.c"

# ── Фиксим #include ─────────────────────────────────────────────────────────
sed -i 's|#include "storage_common.h"|#include "storage_dvd_common.h"|g' \
    "${SRC_DIR}/f_dvd_storage_base.c" \
    "${SRC_DIR}/storage_dvd_common.c"

# ── Применяем патчи ─────────────────────────────────────────────────────────
PATCHES_DIR="${BUILD_DIR}/patches"

run_patch() {
    local target="$1"
    local patch="$2"
    log "  $(basename ${patch}) → $(basename ${target})"
    python3 "${PATCHES_DIR}/apply_patches.py" "${target}" "${patch}"
}

run_patch "${SRC_DIR}/storage_dvd_common.h" "${PATCHES_DIR}/01_num_sectors_type.py"
run_patch "${SRC_DIR}/storage_dvd_common.c" "${PATCHES_DIR}/02_size_limit.py"
run_patch "${SRC_DIR}/f_dvd_storage_base.c" "${PATCHES_DIR}/03_read_toc.py"
run_patch "${SRC_DIR}/f_dvd_storage_base.c" "${PATCHES_DIR}/04_register_commands.py"
run_patch "${SRC_DIR}/f_dvd_storage_base.c" "${PATCHES_DIR}/05_inquiry.py"

log "Подготовка завершена."
