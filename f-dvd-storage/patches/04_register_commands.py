"""
Патч 4: f_dvd_storage_base.c
1. Добавляет #include "dvd_scsi.h" после существующих includes
2. Вставляет case-ы для GET CONFIGURATION (0x46),
   READ DISC INFORMATION (0x51) и READ DVD STRUCTURE (0xAD)
   в switch внутри do_scsi_command()
"""
import re

# Добавляем include dvd_scsi.h
INCLUDE_LINE = '#include "dvd_scsi.h"\n'

# Три новых case-а для do_scsi_command switch
# Вставляем перед SC_READ_10 или SC_READ_6, которые точно есть

GET_CONFIG_CASE = r'''
	case 0x46:		/* GET CONFIGURATION */
		if (!curlun->cdrom)
			goto unknown_cmnd;
		common->data_size_from_cmnd =
				get_unaligned_be16(&common->cmnd[7]);
		reply = check_command(common, 10, DATA_DIR_TO_HOST,
				(0x3 << 1) | (0x3f << 2), 1,
				"GET CONFIGURATION");
		if (reply == 0)
			reply = dvd_do_get_configuration(common, bh);
		break;

	case 0x51:		/* READ DISC INFORMATION */
		if (!curlun->cdrom)
			goto unknown_cmnd;
		common->data_size_from_cmnd =
				get_unaligned_be16(&common->cmnd[7]);
		reply = check_command(common, 10, DATA_DIR_TO_HOST,
				(0x7 << 1), 1,
				"READ DISC INFORMATION");
		if (reply == 0)
			reply = dvd_do_read_disc_information(common, bh);
		break;

	case 0xAD:		/* READ DVD STRUCTURE */
		if (!curlun->cdrom)
			goto unknown_cmnd;
		common->data_size_from_cmnd =
				get_unaligned_be16(&common->cmnd[8]);
		reply = check_command(common, 12, DATA_DIR_TO_HOST,
				(0xf << 2) | (1 << 8), 1,
				"READ DVD STRUCTURE");
		if (reply == 0)
			reply = dvd_do_read_dvd_structure(common, bh);
		break;
'''

def apply(src: str) -> str:
    # --- 1. Добавляем include после последнего #include "*.h" в файле ---
    last_local_include = list(re.finditer(r'^#include\s+"[^"]+\.h"', src, re.MULTILINE))
    if last_local_include:
        pos = last_local_include[-1].end()
        # Не добавляем если уже есть
        if INCLUDE_LINE.strip() not in src:
            src = src[:pos] + '\n' + INCLUDE_LINE + src[pos:]

    # --- 2. Ищем хорошую точку вставки в switch do_scsi_command ---
    # Стратегия: вставляем перед "case SC_READ_10:" или перед "case SC_READ_6:"
    # Оба гарантированно присутствуют в f_mass_storage.c

    inserted = False

    # Вариант А: перед SC_READ_10
    m = re.search(r'(\n\tcase SC_READ_10\s*:)', src)
    if m:
        src = src[:m.start()] + GET_CONFIG_CASE + src[m.start():]
        inserted = True

    # Вариант Б: перед SC_READ_6 (если SC_READ_10 не нашли)
    if not inserted:
        m = re.search(r'(\n\tcase SC_READ_6\s*:)', src)
        if m:
            src = src[:m.start()] + GET_CONFIG_CASE + src[m.start():]
            inserted = True

    if not inserted:
        import sys
        print("  [WARN] 04_register_commands: не нашёл точку вставки SC_READ_10/SC_READ_6",
              file=sys.stderr)
        print("         Добавь вручную case-ы из GET_CONFIG_CASE в do_scsi_command()",
              file=sys.stderr)

    return src
