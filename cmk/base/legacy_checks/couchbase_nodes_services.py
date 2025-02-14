#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.utils.couchbase import parse_couchbase_lines


def discover_couchbase_nodes_services(parsed):
    for key, data in parsed.items():
        yield key, {"discovered_services": data.get("services", [])}


def check_couchbase_nodes_services(item, params, parsed):
    if not (data := parsed.get(item)):
        return
    services_present = set(data.get("services", []))
    services_discovered = set(params["discovered_services"])

    services_appeared = services_present - services_discovered
    services_vanished = services_discovered - services_present
    services_unchanged = services_discovered & services_present

    if services_vanished:
        srt = sorted(services_vanished)
        yield 2, "%d services vanished: %s" % (len(srt), ", ".join(srt))
    if services_appeared:
        srt = sorted(services_appeared)
        yield 2, "%d services appeared: %s" % (len(srt), ", ".join(srt))

    srt = sorted(services_unchanged)
    yield 0, "%d services unchanged: %s" % (len(srt), ", ".join(srt))


check_info["couchbase_nodes_services"] = LegacyCheckDefinition(
    parse_function=parse_couchbase_lines,
    service_name="Couchbase %s Services",
    discovery_function=discover_couchbase_nodes_services,
    check_function=check_couchbase_nodes_services,
)
