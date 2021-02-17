# Copyright (c) 2020-2021 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# export system config action constants

EXPORT_ALL_CONFIG = 'all'
"""Export entire system configuration"""

EXPORT_BIOS_CONFIG = 'BIOS'
"""Export BIOS related configuration"""

EXPORT_IDRAC_CONFIG = 'iDRAC'
"""Export IDRAC related configuration"""

EXPORT_NIC_CONFIG = 'NIC'
"""Export NIC related configuration"""

EXPORT_RAID_CONFIG = 'RAID'
"""Export RAID related configuration"""

# iDRAC Reset action constants


RESET_IDRAC_GRACEFUL_RESTART = 'graceful restart'
"""Perform a graceful shutdown followed by a restart of the system"""

RESET_IDRAC_FORCE_RESTART = 'force restart'
"""Perform an immediate (non-graceful) shutdown, followed by a restart"""