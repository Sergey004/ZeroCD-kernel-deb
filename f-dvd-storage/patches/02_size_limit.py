"""
Патч 2: storage_dvd_common.c
Заменяет жёстко закодированный лимит CD-ROM (~2.1 ГБ) на DVD-9 DL (~8.5 ГБ).

Ищет паттерн вида:
    if (num_sectors >= 256*60*75) {   (или похожий)
        num_sectors = 256*60*75 - 1;
        pr_warn(...);
    }
"""
import re

# DVD-9 DL = 4,173,824 секторов × 2048 байт = 8,548,147,200 байт (~8.5 ГБ)
DVD9_LIMIT = 4173824

def apply(src: str) -> str:
    # Вставляем define после блока #include-ов (перед первой функцией)
    define_str = (
        '\n'
        '/* DVD-9 DL maximum sectors (2048-byte logical blocks) */\n'
        '#define FSG_MAX_DVD9_SECTORS  4173824ULL\n'
        '\n'
    )
    # Ищем место после последнего #include
    last_include = list(re.finditer(r'^#include\s+[<"][^>"]+[>"]', src, re.MULTILINE))
    if last_include:
        pos = last_include[-1].end()
        src = src[:pos] + '\n' + define_str + src[pos:]

    # Паттерн 1: 256*60*75 (старые ядра)
    src = re.sub(
        r'if\s*\(\s*num_sectors\s*>=\s*256\s*\*\s*60\s*\*\s*75\s*\)\s*\{[^}]+\}',
        _replacement,
        src,
        flags=re.DOTALL
    )

    # Паттерн 2: явное число 1152000 (256*60*75 = 1152000)
    src = re.sub(
        r'if\s*\(\s*num_sectors\s*>=\s*1152000\s*\)\s*\{[^}]+\}',
        _replacement,
        src,
        flags=re.DOTALL
    )

    return src

def _replacement(m: 're.Match') -> str:
    return (
        'if (num_sectors >= FSG_MAX_DVD9_SECTORS) {\n'
        '\t\t\tnum_sectors = FSG_MAX_DVD9_SECTORS - 1;\n'
        '\t\t\tpr_warn("optical image exceeds DVD-9 DL limit, clamping\\n");\n'
        '\t\t}'
    )
