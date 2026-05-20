#!/usr/bin/env bash
# /usr/lib/f-dvd-storage/udc-up.sh
# Вызывается udev при появлении UDC.
# Создаёт configfs gadget и подключает образ из /etc/dvd-gadget/image.iso
#
# Аргумент $1: имя UDC (напр. 20980000.usb)

set -euo pipefail

UDC="${1:-}"
CONFIG_ISO="/etc/dvd-gadget/image.iso"
GADGET_NAME="dvd_gadget"
GADGET_PATH="/sys/kernel/config/usb_gadget/$GADGET_NAME"

logger -t f-dvd-storage "udc-up: UDC=$UDC"

# Нет образа — молча выходим
[ -f "$CONFIG_ISO" ] || { logger -t f-dvd-storage "udc-up: $CONFIG_ISO не найден, пропускаем"; exit 0; }

# Уже настроен
[ -d "$GADGET_PATH" ] && exit 0

# Модуль должен быть загружен (DKMS + modules-load.d делают это раньше)
modprobe libcomposite  2>/dev/null || true
modprobe f_dvd_storage 2>/dev/null || true

# configfs должен быть смонтирован
mountpoint -q /sys/kernel/config || mount -t configfs none /sys/kernel/config

mkdir -p "$GADGET_PATH"
echo 0x1d6b > "$GADGET_PATH/idVendor"   # Linux Foundation
echo 0x0104 > "$GADGET_PATH/idProduct"  # Multifunction

mkdir -p "$GADGET_PATH/strings/0x409"
echo "ZeroCD"       > "$GADGET_PATH/strings/0x409/manufacturer"
echo "DVD Gadget"   > "$GADGET_PATH/strings/0x409/product"
echo "000000000001" > "$GADGET_PATH/strings/0x409/serialnumber"

mkdir -p "$GADGET_PATH/functions/dvd_storage.0"
LUN="$GADGET_PATH/functions/dvd_storage.0/lun.0"
mkdir -p "$LUN"
echo 1            > "$LUN/cdrom"
echo 1            > "$LUN/ro"
echo 1            > "$LUN/removable"
echo "$CONFIG_ISO" > "$LUN/file"

mkdir -p "$GADGET_PATH/configs/c.1/strings/0x409"
echo "DVD Config" > "$GADGET_PATH/configs/c.1/strings/0x409/configuration"
echo 120          > "$GADGET_PATH/configs/c.1/MaxPower"

ln -sf "$GADGET_PATH/functions/dvd_storage.0" \
       "$GADGET_PATH/configs/c.1/dvd_storage.0"

echo "$UDC" > "$GADGET_PATH/UDC"
logger -t f-dvd-storage "udc-up: gadget подключён к $UDC с образом $CONFIG_ISO"
