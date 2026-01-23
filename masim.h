#ifndef _MASIM_H
#define _MASIM_H

#define MAX_THREADS 128

struct mregion {
	char name[256];
	size_t sz;
	char *region;
	char *data_file;

	size_t sub_sz;
};

enum rw_mode {
	READ_ONLY,
	WRITE_ONLY,
	READ_WRITE,
};

struct access {
	struct mregion *mregion;
	int random_access;
	size_t stride;
	int probability;
	enum rw_mode rw_mode;

	/* For runtime only */
	int prob_start;
	size_t last_offset[MAX_THREADS];
};

struct phase {
	char *name;
	unsigned time_ms;
	struct access *patterns;
	int nr_patterns;

	/* For runtime only */
	int total_probability;
};

#endif /* _MASIM_H */
