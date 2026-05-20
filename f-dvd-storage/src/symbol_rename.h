/* SPDX-License-Identifier: GPL-2.0 */
/*
 * symbol_rename.h — переименовываем экспортируемые символы
 * чтобы f_dvd_storage.ko не конфликтовал с f_mass_storage.ko
 *
 * Включается через ccflags-y += -include symbol_rename.h
 * (применяется ко всем .c файлам модуля автоматически)
 */
#ifndef _DVD_SYMBOL_RENAME_H
#define _DVD_SYMBOL_RENAME_H

/*
 * Переименовываем все публичные символы из storage_common.c
 * и f_mass_storage.c которые могут экспортироваться через EXPORT_SYMBOL.
 *
 * Конвенция: fsg_* → dvd_fsg_*
 */
#define fsg_lun_open             dvd_fsg_lun_open
#define fsg_lun_close            dvd_fsg_lun_close
#define fsg_lun_fsync_sub        dvd_fsg_lun_fsync_sub
#define fsg_show_ro              dvd_fsg_show_ro
#define fsg_show_nofua           dvd_fsg_show_nofua
#define fsg_show_file            dvd_fsg_show_file
#define fsg_store_ro             dvd_fsg_store_ro
#define fsg_store_nofua          dvd_fsg_store_nofua
#define fsg_store_file           dvd_fsg_store_file
#define fsg_common_get           dvd_fsg_common_get
#define fsg_common_put           dvd_fsg_common_put
#define fsg_common_create_lun    dvd_fsg_common_create_lun
#define fsg_common_remove_lun    dvd_fsg_common_remove_lun
#define fsg_common_create_luns   dvd_fsg_common_create_luns
#define fsg_common_remove_luns   dvd_fsg_common_remove_luns
#define fsg_common_free_luns     dvd_fsg_common_free_luns
#define fsg_common_set_cdev      dvd_fsg_common_set_cdev
#define fsg_common_set_sysfs     dvd_fsg_common_set_sysfs
#define fsg_common_set_num_buffers dvd_fsg_common_set_num_buffers
#define fsg_common_set_inquiry_string dvd_fsg_common_set_inquiry_string
#define fsg_common_run_thread    dvd_fsg_common_run_thread
#define fsg_alloc_inst           dvd_fsg_alloc_inst
#define fsg_free_inst            dvd_fsg_free_inst
#define fsg_bind                 dvd_fsg_bind
#define fsg_unbind               dvd_fsg_unbind
#define fsg_set_alt              dvd_fsg_set_alt
#define fsg_disable              dvd_fsg_disable
#define fsg_suspend              dvd_fsg_suspend
#define fsg_resume               dvd_fsg_resume
#define fsg_func_to_fsg          dvd_fsg_func_to_fsg

/* Configfs и sysfs атрибуты */
#define fsg_lun_dev_type         dvd_fsg_lun_dev_type
#define fsg_lun_attr_ro          dvd_fsg_lun_attr_ro
#define fsg_lun_attr_nofua       dvd_fsg_lun_attr_nofua
#define fsg_lun_attr_file        dvd_fsg_lun_attr_file

/* Имя configfs функции (строка) — чтобы в /sys/kernel/config/usb_gadget/
 * функция регистрировалась как "dvd_storage" а не "mass_storage" */
#define FSG_FUNCTION_NAME        "dvd_storage"

#endif /* _DVD_SYMBOL_RENAME_H */
