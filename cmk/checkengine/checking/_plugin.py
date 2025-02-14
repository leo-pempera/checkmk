#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import NamedTuple, Protocol

from cmk.utils.hostaddress import HostName
from cmk.utils.labels import ServiceLabel
from cmk.utils.rulesets import RuleSetName
from cmk.utils.servicename import ServiceName

from cmk.checkengine.checkresults import ServiceCheckResult
from cmk.checkengine.fetcher import HostKey
from cmk.checkengine.legacy import LegacyCheckParameters
from cmk.checkengine.parameters import TimespecificParameters
from cmk.checkengine.sectionparser import ParsedSectionName, Provider

from ._name import CheckPluginName, Item

__all__ = ["AggregatedResult", "CheckPlugin", "ConfiguredService", "ServiceID"]


class ServiceID(NamedTuple):
    name: CheckPluginName
    item: Item


class ConfiguredService(NamedTuple):
    """A service with all information derived from the config"""

    check_plugin_name: CheckPluginName
    item: Item
    description: ServiceName
    parameters: TimespecificParameters
    # Explicitly optional b/c enforced services don't have disocvered params.
    discovered_parameters: LegacyCheckParameters | None
    service_labels: Mapping[str, ServiceLabel]
    is_enforced: bool

    def id(self) -> ServiceID:
        return ServiceID(self.check_plugin_name, self.item)

    def sort_key(self) -> ServiceID:
        """Allow to sort services

        Basically sort by id(). Unfortunately we have plugins with *AND* without
        items.
        """
        return ServiceID(self.check_plugin_name, self.item or "")


@dataclass(frozen=True)
class AggregatedResult:
    service: ConfiguredService
    submit: bool
    data_received: bool
    result: ServiceCheckResult
    cache_info: tuple[int, int] | None


class CheckFunction(Protocol):
    def __call__(
        self,
        host_name: HostName,
        service: ConfiguredService,
        *,
        providers: Mapping[HostKey, Provider],
    ) -> AggregatedResult:
        ...


@dataclass(frozen=True)
class CheckPlugin:
    sections: Sequence[ParsedSectionName]
    function: CheckFunction
    default_parameters: Mapping[str, object] | None
    ruleset_name: RuleSetName | None
