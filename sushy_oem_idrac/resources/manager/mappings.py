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

from sushy import utils

from sushy_oem_idrac.resources.manager import constants as mgr_cons

EXPORT_CONFIG_VALUE_MAP = {
    'ALL': mgr_cons.EXPORT_ALL_CONFIG,
    'BIOS': mgr_cons.EXPORT_BIOS_CONFIG,
    'IDRAC': mgr_cons.EXPORT_IDRAC_CONFIG,
    'NIC': mgr_cons.EXPORT_NIC_CONFIG,
    'RAID': mgr_cons.EXPORT_RAID_CONFIG
}

EXPORT_CONFIG_VALUE_MAP_REV = utils.revert_dictionary(EXPORT_CONFIG_VALUE_MAP)

RESET_IDRAC_VALUE_MAP = {
    'Graceful': mgr_cons.RESET_IDRAC_GRACEFUL_RESTART,
    'Force': mgr_cons.RESET_IDRAC_FORCE_RESTART,
}

RESET_IDRAC_VALUE_MAP_REV = utils.revert_dictionary(RESET_IDRAC_VALUE_MAP)