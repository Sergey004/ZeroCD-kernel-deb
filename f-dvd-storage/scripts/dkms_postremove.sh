#!/usr/bin/env bash
# scripts/dkms_postremove.sh
set -euo pipefail

log() { echo "[f-dvd-storage postremove] $*"; }

# Удаляем только если пакет полностью удалён (не при обновлении)
# DKMS вызывает postremove при dkms remove, но не при dkms install нового

# Не удаляем blacklist и udev автоматически — это делает debian postrm
log "Модуль выгружен из DKMS. Конфиги в /etc сохранены."
log "Полное удаление: sudo apt purge f-dvd-storage-dkms"
