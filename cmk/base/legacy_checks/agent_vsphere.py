#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# {
#     'tcp_port': 443,
#     'secret': 'wef',
#     'infos': ['hostsystem', 'virtualmachine'],
#     'user': 'wefwef'
# }


# mypy: disable-error-code="list-item"

from typing import Any, Mapping, Optional, Sequence, Union

from cmk.base.check_api import passwordstore_get_cmdline
from cmk.base.config import special_agent_info


def agent_vsphere_arguments(  # pylint: disable=too-many-branches
    params: Mapping[str, Any], hostname: str, ipaddress: Optional[str]
) -> Sequence[Union[str, tuple[str, str, str]]]:
    args = []
    if "tcp_port" in params:
        args += ["-p", "%d" % params["tcp_port"]]

    args += ["-u", params["user"]]
    args += [passwordstore_get_cmdline("-s=%s", params["secret"])]
    args += ["-i", ",".join(params["infos"])]

    #  True: Queried host is a host system
    #  False: Queried host is the vCenter
    if params["direct"]:
        args += ["--direct", "--hostname", hostname]

    if params.get("skip_placeholder_vms", True):
        args.append("-P")

    if "spaces" in params:
        args += ["--spaces", params["spaces"]]

    if "timeout" in params:
        args += ["--timeout", params["timeout"]]

    if v_display := params.get("vm_pwr_display"):
        args += ["--vm_pwr_display", v_display]

    if vm_piggyname := params.get("vm_piggyname"):
        args += ["--vm_piggyname", vm_piggyname]

    if h_display := params.get("host_pwr_display"):
        args += ["--host_pwr_display", h_display]

    if params.get("snapshots_on_host", False):
        args += ["--snapshots-on-host"]

    cert_verify = params.get("ssl", True)
    if cert_verify is False:
        args += ["--no-cert-check"]
    elif cert_verify is True:
        args += ["--cert-server-name", hostname]
    else:
        args += ["--cert-server-name", cert_verify]

    args.append(ipaddress or hostname)

    return args


special_agent_info["vsphere"] = agent_vsphere_arguments
