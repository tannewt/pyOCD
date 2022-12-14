# pyOCD debugger
# Copyright (c) 2015-2020 Arm Limited
# Copyright (c) 2021 Chris Reed
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from inspect import getfullargspec
from typing import (Optional, TYPE_CHECKING)

from ..core.target import Target
from ..core.memory_map import (FlashRegion, MemoryType, RamRegion, DeviceRegion, MemoryMap)
from ..core.soc_target import SoCTarget
from ..utility.sequencer import CallSequence

if TYPE_CHECKING:
    from ..core.session import Session
    from ..core.memory_map import MemoryMap

LOG = logging.getLogger(__name__)

class RiscvTarget(SoCTarget):
    """@brief Represents an SoC that uses RISC-V debug infrastructure.

    Documented here: https://github.com/riscv/riscv-debug-spec

    This class adds RISC-V-specific discovery and initialization code to SoCTarget.
    """

    def __init__(self, session: "Session", memory_map: Optional["MemoryMap"] = None) -> None:
        super().__init__(session, memory_map)
        assert session.probe

        LOG.info("Hello world")

    def create_init_sequence(self) -> CallSequence:
        seq = CallSequence(
            ('load_svd',            self.load_svd),
            ('pre_connect',         self.pre_connect),
            ('dp_init',             self.dp.create_connect_sequence),
            ('create_discoverer',   self.create_discoverer),
            ('discovery',           lambda : self._discoverer.discover() if self._discoverer else None),
            ('check_for_cores',     self.check_for_cores),
            ('halt_on_connect',     self.perform_halt_on_connect),
            ('post_connect',        self.post_connect),
            ('post_connect_hook',   self.post_connect_hook),
            ('create_flash',        self.create_flash),
            ('notify',              lambda : self.session.notify(Target.Event.POST_CONNECT, self))
            )

        return seq
