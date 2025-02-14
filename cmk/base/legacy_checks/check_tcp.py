#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="list-item"

from cmk.base.config import active_check_info


def check_tcp_arguments(params):  # pylint: disable=too-many-branches
    port, settings = params
    args = []

    args += ["-p", str(port)]

    if "response_time" in settings:
        warn, crit = settings["response_time"]
        args += ["-w", "%f" % (warn / 1000.0)]
        args += ["-c", "%f" % (crit / 1000.0)]

    if "timeout" in settings:
        args += ["-t", settings["timeout"]]

    if "refuse_state" in settings:
        args += ["-r", settings["refuse_state"]]

    if settings.get("escape_send_string"):
        args.append("--escape")

    if "send_string" in settings:
        args += ["-s", settings["send_string"]]

    if "expect" in settings:
        for s in settings["expect"]:
            args += ["-e", s]

    if settings.get("expect_all"):
        args.append("-A")

    if settings.get("jail"):
        args.append("--jail")

    if "mismatch_state" in settings:
        args += ["-M", settings["mismatch_state"]]

    if "delay" in settings:
        args += ["-d", settings["delay"]]

    if "maxbytes" in settings:
        args += ["-m", settings["maxbytes"]]

    if settings.get("ssl"):
        args.append("--ssl")

    if "cert_days" in settings:
        # legacy behavior
        if isinstance(settings["cert_days"], int):
            args += ["-D", settings["cert_days"]]
        else:
            warn, crit = settings["cert_days"]
            args += ["-D", "%d,%d" % (warn, crit)]

    if "quit_string" in settings:
        args += ["-q", settings["quit_string"]]

    if "hostname" in settings:
        args += ["-H", settings["hostname"]]
    else:
        args += ["-H", "$HOSTADDRESS$"]

    return args


active_check_info["tcp"] = {
    "command_line": "check_tcp $ARG1$",
    "argument_function": check_tcp_arguments,
    "service_description": lambda args: args[1].get("svc_description", "TCP Port %d" % args[0]),
}
