# Makefile для DKMS сборки f_dvd_storage
#
# DKMS передаёт переменные:
#   KERNELRELEASE  — версия ядра (напр. 6.12.25+rpt-rpi-v8)
#   KERNEL_ARCH    — архитектура (arm64)
#
# При нативной сборке (прямо на Pi) CROSS_COMPILE пустой.
# При кросс-сборке DKMS не используется — используй build.sh.

KVER   ?= $(KERNELRELEASE)
KDIR   ?= /lib/modules/$(KVER)/build

ccflags-y += -I$(src)/src
ccflags-y += -DCONFIG_USB_GADGET_STORAGE_NUM_BUFFERS=2
ccflags-y += -DDVD_GADGET_MODULE
ccflags-y += -include $(src)/src/symbol_rename.h
ccflags-y += -Wno-unused-variable -Wno-unused-function

obj-m := f_dvd_storage.o
f_dvd_storage-objs := \
	src/storage_dvd_common.o \
	src/f_dvd_storage_base.o \
	src/dvd_scsi.o

all:
	$(MAKE) -C $(KDIR) M=$(shell pwd) modules

clean:
	$(MAKE) -C $(KDIR) M=$(shell pwd) clean

.PHONY: all clean
