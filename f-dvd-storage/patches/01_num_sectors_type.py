"""
Патч 1: storage_common.h
Меняет тип поля num_sectors в struct fsg_lun с u32 на loff_t.
"""
import re

def apply(src: str) -> str:
    # Заменяем объявление поля num_sectors в структуре fsg_lun
    # Оригинал: "\tu32\t\tnum_sectors;" или "\tu32 num_sectors;"
    patched = re.sub(
        r'(\bstruct fsg_lun\b.*?})',
        _patch_struct,
        src,
        flags=re.DOTALL
    )
    return patched

def _patch_struct(m: 're.Match') -> str:
    struct_body = m.group(0)
    # Заменяем u32 num_sectors на loff_t num_sectors
    result = re.sub(
        r'\bu32\b(\s+num_sectors\s*;)',
        r'loff_t\1  /* DVD: loff_t to support >2GB images */',
        struct_body
    )
    return result
