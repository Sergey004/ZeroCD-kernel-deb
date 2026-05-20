#!/usr/bin/env bash
# /usr/lib/f-dvd-storage/udc-down.sh
set -euo pipefail

GADGET_PATH="/sys/kernel/config/usb_gadget/dvd_gadget"
[ -d "$GADGET_PATH" ] || exit 0

logger -t f-dvd-storage "udc-down: отключаем gadget"

echo "" > "$GADGET_PATH/UDC" 2>/dev/null || true
rm -f  "$GADGET_PATH/configs/c.1/dvd_storage.0"
rmdir  "$GADGET_PATH/configs/c.1/strings/0x409" 2>/dev/null || true
rmdir  "$GADGET_PATH/configs/c.1"               2>/dev/null || true
rmdir  "$GADGET_PATH/functions/dvd_storage.0/lun.0" 2>/dev/null || true
rmdir  "$GADGET_PATH/functions/dvd_storage.0"   2>/dev/null || true
rmdir  "$GADGET_PATH/strings/0x409"             2>/dev/null || true
rmdir  "$GADGET_PATH"                           2>/dev/null || true
