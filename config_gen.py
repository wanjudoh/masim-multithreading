#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0

prog_description = '''
MASIM config generator for hot-region experiments.

- 100 regions, each 1GB
- 10 phases, each 1 minute
- Hot region behavior controlled by arguments
'''

import argparse
import random
import masim_config

NR_REGIONS = 100
REGION_SIZE_BYTES = 1 * 1024 * 1024 * 1024  # 1GB
PHASE_RUNTIME_MS = 60_000                   # 1 minute
NR_PHASES = 10

# Hotness values (accesses per msec, relative)
COLD_HOTNESS = 1
HOT_HOTNESS_BASE = 50   # baseline hotness for hot regions

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mode', choices=['static', 'dynamic'], required=True,
        help='hot regions fixed (static) or change every phase (dynamic)')
    parser.add_argument(
        '--nr_hot', type=int, required=True,
        help='number of hot regions')
    parser.add_argument(
        '--hotness', choices=['same', 'diff'], required=True,
        help='all hot regions same hotness or different hotness')
    parser.description = prog_description
    return parser.parse_args()

def main():
    args = parse_args()

    if args.nr_hot <= 0 or args.nr_hot > NR_REGIONS:
        raise ValueError('nr_hot must be between 1 and 100')

    # --------------------
    # Define regions
    # --------------------
    regions = []
    for i in range(NR_REGIONS):
        regions.append(
            masim_config.Region(
                name=f'r{i}',
                sz_bytes=REGION_SIZE_BYTES,
                init_data_file=None
            )
        )

    init_patterns = []
    for region_idx, region in enumerate(regions):
        init_patterns.append(
            masim_config.AccessPattern(
                region_name=region.name,
                randomness=True,
                stride=4096,
                access_probability=1,
                rw_mode='wo'
            )
        )

    phases = []
    init_phase = masim_config.Phase(
        name='init_phase',
        runtime_ms=PHASE_RUNTIME_MS,
        patterns=init_patterns
    )
    phases.append(init_phase)

    # --------------------
    # Decide hot regions
    # --------------------
    if args.mode == 'static':
        static_hot_regions = random.sample(range(NR_REGIONS), args.nr_hot)

    for phase_idx in range(NR_PHASES):
        patterns = []

        # Select hot regions
        if args.mode == 'dynamic':
            hot_regions = random.sample(range(NR_REGIONS), args.nr_hot)
        else:
            hot_regions = static_hot_regions

        # Assign hotness
        if args.hotness == 'same':
            hotness_map = {
                r: HOT_HOTNESS_BASE for r in hot_regions
            }
        else:
            hotness_map = {
                r: HOT_HOTNESS_BASE + i * 10
                for i, r in enumerate(hot_regions)
            }

        for region_idx, region in enumerate(regions):
            if region_idx in hot_regions:
                access_prob = hotness_map[region_idx]
            else:
                access_prob = COLD_HOTNESS

            patterns.append(
                masim_config.AccessPattern(
                    region_name=region.name,
                    randomness=True,
                    stride=4096,
                    access_probability=access_prob,
                    rw_mode='ro'
                )
            )

        phases.append(
            masim_config.Phase(
                name=f'phase{phase_idx}',
                runtime_ms=PHASE_RUNTIME_MS,
                patterns=patterns
            )
        )

    masim_config.pr_config(regions, phases)

if __name__ == '__main__':
    main()
