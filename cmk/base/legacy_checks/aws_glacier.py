#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Iterable, Mapping

from cmk.base.check_api import check_levels, get_bytes_human_readable, LegacyCheckDefinition
from cmk.base.check_legacy_includes.aws import parse_aws
from cmk.base.config import check_info

Section = Mapping[str, Mapping]


def parse_aws_glacier(string_table):
    parsed = parse_aws(string_table)
    parsed_by_vault = {}
    for vault in parsed:
        parsed_by_vault[vault["VaultName"]] = vault
    return parsed_by_vault


# .
#   .--Glacier archives----------------------------------------------------.
#   |                    ____ _            _                               |
#   |                   / ___| | __ _  ___(_) ___ _ __                     |
#   |                  | |  _| |/ _` |/ __| |/ _ \ '__|                    |
#   |                  | |_| | | (_| | (__| |  __/ |                       |
#   |                   \____|_|\__,_|\___|_|\___|_|                       |
#   |                               _     _                                |
#   |                 __ _ _ __ ___| |__ (_)_   _____  ___                 |
#   |                / _` | '__/ __| '_ \| \ \ / / _ \/ __|                |
#   |               | (_| | | | (__| | | | |\ V /  __/\__ \                |
#   |                \__,_|_|  \___|_| |_|_| \_/ \___||___/                |
#   |                                                                      |
#   '----------------------------------------------------------------------'


def inventory_aws_glacier(parsed):
    for vault_name in parsed:
        yield vault_name, {}


def check_aws_glacier_archives(item, params, parsed):
    if not (data := parsed.get(item)):
        return
    vault_size = data.get("SizeInBytes", 0)
    yield check_levels(
        vault_size,
        "aws_glacier_vault_size",
        params.get("vault_size_levels", (None, None)),
        human_readable_func=get_bytes_human_readable,
        infoname="Vault size",
    )

    num_archives = data.get("NumberOfArchives", 0)
    yield 0, "Number of archives: %s" % int(num_archives), [
        ("aws_glacier_num_archives", num_archives)
    ]

    tag_infos = []
    for key, value in list(data.get("Tagging", {}).items()):
        tag_infos.append("%s: %s" % (key, value))
    if tag_infos:
        yield 0, "[Tags]: %s" % ", ".join(tag_infos)


check_info["aws_glacier"] = LegacyCheckDefinition(
    parse_function=parse_aws_glacier,
    service_name="AWS/Glacier Vault: %s",
    discovery_function=inventory_aws_glacier,
    check_function=check_aws_glacier_archives,
    check_ruleset_name="aws_glacier_vault_archives",
)

# .
#   .--Glacier summary-----------------------------------------------------.
#   |                    ____ _            _                               |
#   |                   / ___| | __ _  ___(_) ___ _ __                     |
#   |                  | |  _| |/ _` |/ __| |/ _ \ '__|                    |
#   |                  | |_| | | (_| | (__| |  __/ |                       |
#   |                   \____|_|\__,_|\___|_|\___|_|                       |
#   |           ___ _   _ _ __ ___  _ __ ___   __ _ _ __ _   _             |
#   |          / __| | | | '_ ` _ \| '_ ` _ \ / _` | '__| | | |            |
#   |          \__ \ |_| | | | | | | | | | | | (_| | |  | |_| |            |
#   |          |___/\__,_|_| |_| |_|_| |_| |_|\__,_|_|   \__, |            |
#   |                                                    |___/             |
#   '----------------------------------------------------------------------


def discover_aws_glacier_summary(section: Section) -> Iterable[tuple[None, dict]]:
    if section:
        yield None, {}


def check_aws_glacier_summary(item, params, parsed):
    sum_size = 0
    largest_vault = None
    largest_vault_size = 0
    for vault_name in sorted(parsed):
        vault_size = parsed.get(vault_name).get("SizeInBytes", 0)
        sum_size += vault_size
        if vault_size >= largest_vault_size:
            largest_vault = vault_name
            largest_vault_size = vault_size
    yield check_levels(
        sum_size,
        "aws_glacier_total_vault_size",
        params.get("vault_size_levels", (None, None)),
        human_readable_func=get_bytes_human_readable,
        infoname="Total size",
    )

    if largest_vault:
        yield 0, "Largest vault: %s (%s)" % (
            largest_vault,
            get_bytes_human_readable(largest_vault_size),
        ), [("aws_glacier_largest_vault_size", largest_vault_size)]


check_info["aws_glacier.summary"] = LegacyCheckDefinition(
    service_name="AWS/Glacier Summary",
    sections=["aws_glacier"],
    discovery_function=discover_aws_glacier_summary,
    check_function=check_aws_glacier_summary,
    check_ruleset_name="aws_glacier_vaults",
)
