"""
Патч 5: f_dvd_storage_base.c
Меняет INQUIRY: для образов > 450000 секторов (~900 МБ) возвращает
"File-DVD Gadget" вместо "File-CD Gadget" и version=SPC-3.
"""
import re

NEW_INQUIRY_STRINGS = '''
	is_dvd = curlun->cdrom && (curlun->num_sectors > 450000);

	buf[2] = is_dvd ? 0x05 : 0x02;	/* SPC-3 for DVD, SCSI-2 for CD */
	buf[3] = 0x02;			/* Response Data Format */
	buf[4] = 31;
	/* buf[5..7] reserved */
	sprintf(buf + 8, "%-8s", "Linux   ");
	if (!curlun->cdrom)
		sprintf(buf + 16, "%-16s", "File-Stor Gadget");
	else if (is_dvd)
		sprintf(buf + 16, "%-16s", "File-DVD Gadget ");
	else
		sprintf(buf + 16, "%-16s", "File-CD Gadget  ");
	sprintf(buf + 32, "%-4s", "0000");
	return 36;
'''

def apply(src: str) -> str:
    # Ищем do_inquiry, внутри неё блок с "File-CD Gadget"
    # Заменяем всё от "buf[2] = 2;" (или "buf[2] = 0x02;")
    # до "return 36;"
    pattern = re.compile(
        r'(static int do_inquiry.*?memset\(buf, 0, 36\);)'  # до memset
        r'(.*?)'                                             # заменяем этот кусок
        r'(return 36;\s*\n)',
        re.DOTALL
    )

    def replacer(m):
        before = m.group(1)
        after  = m.group(3)
        # Добавляем объявление is_dvd перед memset или после него
        # Находим место для bool is_dvd
        bool_decl = '\tbool\t\tis_dvd;\n'
        # Вставляем объявление до memset
        before_with_decl = re.sub(
            r'(\tmemset\(buf, 0, 36\);)',
            bool_decl + r'\1',
            before
        )
        return before_with_decl + NEW_INQUIRY_STRINGS + after

    new_src = pattern.sub(replacer, src, count=1)

    if new_src == src:
        # Более простой фолбэк: просто заменяем строки с продуктами
        new_src = src.replace(
            '"File-CD Gadget  "',
            'is_dvd ? "File-DVD Gadget " : "File-CD Gadget  "'
        )

    return new_src
