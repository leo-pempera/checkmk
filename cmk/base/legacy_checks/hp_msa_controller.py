#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.cpu_util import check_cpu_util
from cmk.base.check_legacy_includes.hp_msa import parse_hp_msa
from cmk.base.config import check_info

# <<<hp_msa_controller>>>
# controller-statistics 1 durable-id controller_A
# controller-statistics 1 cpu-load 3
# controller-statistics 1 power-on-time 7855017
# controller-statistics 1 write-cache-used 24
# controller-statistics 1 bytes-per-second 6434.3KB
# controller-statistics 1 bytes-per-second-numeric 6434304
# controller-statistics 1 iops 184
# controller-statistics 1 number-of-reads 67423711
# controller-statistics 1 read-cache-hits 86626091
# controller-statistics 1 read-cache-misses 172382632
# controller-statistics 1 number-of-writes 500652138
# controller-statistics 1 write-cache-hits 281297065
# controller-statistics 1 write-cache-misses 1063951139
# controller-statistics 1 data-read 7711.4GB
# controller-statistics 1 data-read-numeric 7711480795648
# controller-statistics 1 data-written 40.8TB
# controller-statistics 1 data-written-numeric 40830379518976
# controller-statistics 1 num-forwarded-cmds 1
# controller-statistics 1 reset-time 2015-05-22 13:54:37
# controller-statistics 1 reset-time-numeric 1432302877
# controller-statistics 1 start-sample-time 2015-08-21 11:51:52
# controller-statistics 1 start-sample-time-numeric 1440157912
# controller-statistics 1 stop-sample-time 2015-08-21 11:51:57
# controller-statistics 1 stop-sample-time-numeric 1440157917
# controller-statistics 1 total-power-on-hours 2636.59

#   .--controller cpu------------------------------------------------------.
#   |                   _             _ _                                  |
#   |    ___ ___  _ __ | |_ _ __ ___ | | | ___ _ __    ___ _ __  _   _     |
#   |   / __/ _ \| '_ \| __| '__/ _ \| | |/ _ \ '__|  / __| '_ \| | | |    |
#   |  | (_| (_) | | | | |_| | | (_) | | |  __/ |    | (__| |_) | |_| |    |
#   |   \___\___/|_| |_|\__|_|  \___/|_|_|\___|_|     \___| .__/ \__,_|    |
#   |                                                     |_|              |
#   +----------------------------------------------------------------------+
#   |                           main check                                 |
#   '----------------------------------------------------------------------'


def inventory_hp_msa_controller_cpu(parsed):
    for key in parsed:
        yield key, {}


def check_hp_msa_controller_cpu(item, params, parsed):
    if item in parsed:
        # hp msa 2040 reference guide:
        # cpu-load: percentage of time the CPU is busy, from 0-100
        return check_cpu_util(float(parsed[item]["cpu-load"]), params)
    return None


check_info["hp_msa_controller"] = LegacyCheckDefinition(
    parse_function=parse_hp_msa,
    service_name="CPU Utilization %s",
    discovery_function=inventory_hp_msa_controller_cpu,
    check_function=check_hp_msa_controller_cpu,
    check_ruleset_name="cpu_utilization_multiitem",
    check_default_parameters={
        "levels": (80.0, 90.0),
    },
)
