/* SPDX-License-Identifier: GPL-2.0 */
/*
 * dvd_scsi.h — DVD-ROM specific SCSI command handlers
 * for f_dvd_storage out-of-tree module
 *
 * Implements:
 *   GET CONFIGURATION   (0x46) — MMC-6 §6.7
 *   READ DISC INFORMATION (0x51) — MMC-6 §6.22
 *   READ DVD STRUCTURE  (0xAD) — MMC-6 §6.28
 */
#ifndef _DVD_SCSI_H
#define _DVD_SCSI_H

#include <linux/types.h>

/* Forward declaration — defined in storage_dvd_common.h (included by base) */
struct fsg_common;
struct fsg_buffhd;

/**
 * dvd_do_get_configuration - respond to GET CONFIGURATION (0x46)
 *
 * Reports current MMC profile. For images > 450000 sectors reports
 * DVD-ROM (0x0010), otherwise CD-ROM (0x0008).
 */
int dvd_do_get_configuration(struct fsg_common *common,
			     struct fsg_buffhd *bh);

/**
 * dvd_do_read_disc_information - respond to READ DISC INFORMATION (0x51)
 *
 * Returns Standard Disc Information indicating a complete, finalized,
 * single-session, single-track disc.
 */
int dvd_do_read_disc_information(struct fsg_common *common,
				 struct fsg_buffhd *bh);

/**
 * dvd_do_read_dvd_structure - respond to READ DVD STRUCTURE (0xAD)
 *
 * Returns Physical Format Information (format 0x00) or Copyright
 * Information (format 0xFF). All other formats return INVALID FIELD.
 */
int dvd_do_read_dvd_structure(struct fsg_common *common,
			      struct fsg_buffhd *bh);

#endif /* _DVD_SCSI_H */
