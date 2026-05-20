#!/usr/bin/env bash
# scripts/dkms_postinstall.sh
# Запускается после установки модуля.
set -euo pipefail

BLACKLIST_FILE="/etc/modprobe.d/f-dvd-storage.conf"
LOAD_FILE="/etc/modules-load.d/f-dvd-storage.conf"

log() { echo "[f-dvd-storage postinstall] $*"; }

# --- Создаём blacklist для стокового f_mass_storage -------------------------
# Оба модуля МОГУТ сосуществовать (разные символы), но на Pi ZeroCD
# нам нужен только наш. Blacklist предотвращает автозагрузку стокового.
if [ ! -f "$BLACKLIST_FILE" ]; then
    log "Создаём $BLACKLIST_FILE ..."
    cat > "$BLACKLIST_FILE" <<'EOF'
# f-dvd-storage: используем f_dvd_storage вместо стокового f_mass_storage
# Если нужен оригинальный — закомментируй следующую строку
blacklist usb_f_mass_storage

# Алиас: modprobe dvd_storage загружает наш модуль
alias dvd_storage f_dvd_storage
EOF
fi

# --- Автозагрузка -----------------------------------------------------------
if [ ! -f "$LOAD_FILE" ]; then
    log "Создаём $LOAD_FILE ..."
    cat > "$LOAD_FILE" <<'EOF'
# f-dvd-storage: автозагрузка DVD gadget модуля
libcomposite
f_dvd_storage
EOF
fi

# --- udev правило для автоматического подключения образа -------------------
UDEV_FILE="/etc/udev/rules.d/89-dvd-gadget.rules"
if [ ! -f "$UDEV_FILE" ]; then
    log "Создаём udev правило $UDEV_FILE ..."
    cat > "$UDEV_FILE" <<'EOF'
# f-dvd-storage: при появлении UDC автоматически включить gadget
# Требует наличия /etc/dvd-gadget/image.iso
ACTION=="add", SUBSYSTEM=="udc", RUN+="/usr/lib/f-dvd-storage/udc-up.sh %k"
ACTION=="remove", SUBSYSTEM=="udc", RUN+="/usr/lib/f-dvd-storage/udc-down.sh %k"
EOF
    udevadm control --reload-rules 2>/dev/null || true
fi

log "Готово. Перезагрузись или: sudo modprobe f_dvd_storage"
