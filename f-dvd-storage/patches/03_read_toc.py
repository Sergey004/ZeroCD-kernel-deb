"""
Патч 3: f_dvd_storage_base.c
Расширяет do_read_toc():
  - format=1 (Multi-Session Information) — нужен для DVD и Windows
  - format=2 (Raw TOC) — запрашивается macOS в legacy SFF8020i формате
  - SFF8020i decode: format bits в cmnd[9] bits 7:6
  - Фикс маски check_command: добавляем cmnd[2] (Format Field)
"""
import re

# Полная замена функции do_read_toc
NEW_DO_READ_TOC = r'''
static int do_read_toc(struct fsg_common *common, struct fsg_buffhd *bh)
{
	struct fsg_lun	*curlun = common->curlun;
	int		msf = common->cmnd[1] & 0x02;
	int		start_track = common->cmnd[6];
	u8		*buf = (u8 *)bh->buf;
	u8		format;
	int		len;

	/*
	 * Decode Format field.
	 * Modern MMC: byte 2 bits 3:0.
	 * Legacy SFF8020i (Mac OS X): byte 9 bits 7:6 when byte 2 == 0.
	 */
	format = common->cmnd[2] & 0x0f;
	if (format == 0 && (common->cmnd[9] & 0xc0))
		format = common->cmnd[9] >> 6;

	if (start_track > 1) {
		curlun->sense_data = SS_INVALID_FIELD_IN_CDB;
		return -EINVAL;
	}

	switch (format) {
	case 0:		/* Formatted TOC */
	case 1:		/* Multi-Session Information — identical for single-session disc */
		len = 4 + 2 * 8;
		memset(buf, 0, len);
		buf[1] = len - 2;	/* TOC Data Length */
		buf[2] = 1;		/* First Track / First Complete Session */
		buf[3] = 1;		/* Last Track  / Last Complete Session  */

		/* Descriptor 0: Track 1 */
		buf[5] = 0x16;		/* ADR=1, CONTROL=6: data, copy permitted */
		buf[6] = 0x01;		/* Track Number */
		store_cdrom_address(&buf[8], msf, 0);

		/* Descriptor 1: Lead-out (0xAA) */
		buf[13] = 0x16;
		buf[14] = 0xAA;
		store_cdrom_address(&buf[16], msf, curlun->num_sectors);
		return len;

	case 2:		/* Raw TOC — requested by Mac OS X in SFF8020i mode */
		/*
		 * Fake a single-session raw Q-channel TOC.
		 * 4-byte header + 3 entries × 11 bytes = 37 bytes.
		 */
		len = 4 + 3 * 11;
		memset(buf, 0, len);
		buf[1] = len - 2;
		buf[2] = 1;	/* First Session */
		buf[3] = 1;	/* Last Session  */

		/* Entry 0: POINT=0xA0 — first track number in session */
		buf[4]  = 1;		/* Session */
		buf[5]  = 0x16;
		buf[6]  = 0x00;		/* TNO */
		buf[7]  = 0xA0;		/* POINT */
		buf[12] = 0x01;		/* PMIN: first track = 1 */
		/* PSEC=0x00: CD-ROM disc type */

		/* Entry 1: POINT=0xA1 — last track number in session */
		buf[15] = 1;
		buf[16] = 0x16;
		buf[18] = 0xA1;
		buf[23] = 0x01;		/* PMIN: last track = 1 */

		/* Entry 2: POINT=0xA2 — lead-out start position */
		buf[26] = 1;
		buf[27] = 0x16;
		buf[29] = 0xA2;
		store_cdrom_address(&buf[33], msf, curlun->num_sectors);
		return len;

	default:	/* PMA, ATIP, CD-TEXT: not required */
		curlun->sense_data = SS_INVALID_FIELD_IN_CDB;
		return -EINVAL;
	}
}
'''

def apply(src: str) -> str:
    # --- 1. Заменяем do_read_toc ---
    # Ищем функцию от объявления до закрывающей }
    pattern = re.compile(
        r'static int do_read_toc\s*\(.*?\n\}',
        re.DOTALL
    )
    m = pattern.search(src)
    if m:
        src = src[:m.start()] + NEW_DO_READ_TOC.strip() + src[m.end():]

    # --- 2. Фиксим маску check_command для READ TOC ---
    # Было: (7<<6) | (1<<1)  или  (0xf<<6) | (1<<1)
    # Надо: (0xf<<6) | (1<<2) | (1<<1)  — разрешаем cmnd[2] (Format)
    src = re.sub(
        r'(reply\s*=\s*check_command\s*\([^,]+,\s*10\s*,\s*DATA_DIR_TO_HOST\s*,\s*)'
        r'\([^)]+\)'
        r'(\s*,\s*1\s*,\s*"READ TOC")',
        r'\1(0xf<<6) | (1<<2) | (1<<1)\2',
        src
    )

    return src
