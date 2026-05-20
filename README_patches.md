# ZeroCD DVD Patch Series
## USB gadget: f_mass_storage DVD-ROM emulation for Raspberry Pi Zero 2 W

### Что делает этот набор патчей

Добавляет полноценную эмуляцию DVD-ROM в `g_mass_storage`. После применения
образы > 2.1 ГБ работают корректно, включая Apple Mac OS X Install DVD с
гибридной HFS+/ISO9660 файловой системой и Boot Camp драйверами.

### Файлы для изменения

```
drivers/usb/gadget/function/f_mass_storage.c
drivers/usb/gadget/function/storage_common.c
drivers/usb/gadget/function/storage_common.h
```

### Порядок применения

```bash
cd /path/to/linux-source
git apply 0001-storage-common-raise-size-limit-to-dvd9.patch
git apply 0002-f_mass_storage-fix-read-toc-multisession-macosx.patch
git apply 0003-f_mass_storage-add-get-configuration.patch
git apply 0004-f_mass_storage-add-read-dvd-structure.patch
git apply 0005-f_mass_storage-add-read-disc-information.patch
git apply 0006-f_mass_storage-fix-inquiry-for-dvd.patch
```

Или через `patch`:
```bash
for p in 000*.patch; do patch -p1 < $p; done
```

### Что реализовано в каждом патче

| Патч | SCSI команда | Что делает |
|------|-------------|------------|
| 0001 | — | Снимает лимит 2.1 ГБ, `num_sectors` → `loff_t` |
| 0002 | READ TOC (0x9E) | Добавляет format=1 (multi-session), format=2 (raw, для macOS), SFF8020i decode |
| 0003 | GET CONFIGURATION (0x46) | Репортит DVD-ROM profile (0x0010) для образов > 900 МБ |
| 0004 | READ DVD STRUCTURE (0xAD) | Physical Format Information (PFI), Copyright Info |
| 0005 | READ DISC INFORMATION (0x51) | Disc state, session/track counts |
| 0006 | INQUIRY (0x12) | "File-DVD Gadget" + SPC-3 version для DVD образов |

### Важные замечания

1. **Офсеты строк** — патчи используют `index XXXXXXX..XXXXXXX` как placeholder.
   При применении `git apply` может потребоваться `--ignore-whitespace` или `--reject`
   если офсеты строк не совпадут из-за версии ядра. В этом случае применяй вручную.

2. **num_sectors тип** — патч 0001 меняет `u32 num_sectors` → `loff_t num_sectors`
   в `struct fsg_lun`. Проверь все места в коде где используется `curlun->num_sectors`
   с форматом `%u` — надо заменить на `%llu` с кастом `(unsigned long long)`.

3. **Apple Mac OS X Install DVD** специально:
   - GET CONFIGURATION → хост видит DVD-ROM profile → шлёт READ DVD STRUCTURE
   - READ TOC format=2 → macOS монтирует HFS+ часть корректно
   - ISO9660/Joliet часть (Boot Camp) доступна из Windows без изменений

4. **Zero 2 W специфика** — Pi Zero 2 W использует USB 2.0 HS (480 Мбит/с).
   Реальный DVD-ROM читает максимум ~22 МБ/с (16x), что укладывается в USB 2.0.
   Для образов на microSD рекомендуется карта класса A1/A2.

### Проверка после сборки

```bash
# Подключить образ
echo "/media/macosx_install.iso" > /sys/kernel/config/usb_gadget/g1/functions/mass_storage.0/lun.0/file
echo 1 > /sys/kernel/config/usb_gadget/g1/functions/mass_storage.0/lun.0/cdrom
echo 1 > /sys/kernel/config/usb_gadget/g1/functions/mass_storage.0/lun.0/ro

# Отладка SCSI команд
echo 1 > /sys/module/usb_storage/parameters/delay_use
# или включить debug в ядре: CONFIG_USB_GADGET_DEBUG_FILES=y
```

### Известные ограничения

- READ DVD STRUCTURE format=0x03 (BCA descriptor) не реализован (не нужен)
- Multi-layer DVD (DVD-9) эмулируется как single-layer с правильным end PSN
- DVD±RW команды не реализованы (только read-only DVD-ROM)
- Blu-ray (профиль 0x0040) не реализован
