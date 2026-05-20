#!/usr/bin/env python3
"""
apply_patches.py — запускает патч-модуль против указанного файла.

Использование: python3 apply_patches.py <target_file> <patch_module.py>

Патч-модуль должен определять функцию:
    def apply(src: str) -> str
которая принимает текст файла и возвращает изменённый текст.
"""
import sys
import importlib.util
import os

def run(target_path: str, patch_path: str) -> None:
    with open(target_path, 'r', encoding='utf-8') as f:
        original = f.read()

    spec = importlib.util.spec_from_file_location("patch_module", patch_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    patched = mod.apply(original)

    if patched == original:
        print(f"  [WARN] {os.path.basename(patch_path)}: нет изменений в {os.path.basename(target_path)}")
        print(f"         Возможно, ядро уже содержит этот патч, или контекст не совпал.")
    else:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(patched)
        lines_changed = sum(
            1 for a, b in zip(original.splitlines(), patched.splitlines()) if a != b
        )
        print(f"  [OK]   {os.path.basename(patch_path)}: ~{lines_changed} строк изменено")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Использование: {sys.argv[0]} <target_file> <patch_module.py>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
