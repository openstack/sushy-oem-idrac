# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
# Copyright (c) 2020-2021 Dell Inc. or its subsidiaries.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
from unittest import mock

from oslotest.base import BaseTestCase
import sushy
from sushy.resources.manager import manager
from sushy.taskmonitor import TaskMonitor

from sushy_oem_idrac.resources.manager import constants as mgr_cons
from sushy_oem_idrac.resources.manager import idrac_card_service as idrac_card
from sushy_oem_idrac.resources.manager import job_collection as jc
from sushy_oem_idrac.resources.manager import job_service as job
from sushy_oem_idrac.resources.manager import lifecycle_service as lifecycle
from sushy_oem_idrac.resources.manager import manager as oem_manager


class ManagerTestCase(BaseTestCase):

    def setUp(self):
        super(ManagerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('sushy_oem_idrac/tests/unit/json_samples/'
                  'manager.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200

        mock_response = self.conn.post.return_value
        mock_response.status_code = 202
        mock_response.headers = {
            'Location': '/redfish/v1/TaskService/Tasks/JID_905749031119'}
        mock_response.content = None

        self.manager = manager.Manager(self.conn, '/redfish/v1/Managers/BMC',
                                       redfish_version='1.0.2')

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_import_system_configuration_uri(self):
        oem = self.manager.get_oem_extension('Dell')

        self.assertEqual(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ImportSystemConfiguration',
            oem.import_system_configuration_uri)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_set_virtual_boot_device_cd(self):
        oem = self.manager.get_oem_extension('Dell')

        oem.set_virtual_boot_device(
            sushy.VIRTUAL_MEDIA_CD, manager=self.manager)

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ImportSystemConfiguration', data=mock.ANY)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_allowed_export_target_values(self):
        oem = self.manager.get_oem_extension('Dell')
        expected_values = {mgr_cons.EXPORT_TARGET_IDRAC,
                           mgr_cons.EXPORT_TARGET_RAID,
                           mgr_cons.EXPORT_TARGET_ALL,
                           mgr_cons.EXPORT_TARGET_BIOS,
                           mgr_cons.EXPORT_TARGET_NIC}
        allowed_values = oem.get_allowed_export_target_values()
        self.assertEqual(expected_values, allowed_values)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_allowed_export_target_values_missing(self):
        oem = self.manager.get_oem_extension('Dell')
        export_action = ('OemManager.v1_0_0'
                         '#OemManager.ExportSystemConfiguration')
        oem.json['Actions']['Oem'][export_action]['ShareParameters'].pop(
            'Target@Redfish.AllowableValues')
        oem.refresh()
        oem = self.manager.get_oem_extension('Dell')
        expected_values = {mgr_cons.EXPORT_TARGET_IDRAC,
                           mgr_cons.EXPORT_TARGET_RAID,
                           mgr_cons.EXPORT_TARGET_ALL,
                           mgr_cons.EXPORT_TARGET_BIOS,
                           mgr_cons.EXPORT_TARGET_NIC}
        allowed_values = oem.get_allowed_export_target_values()
        self.assertEqual(expected_values, allowed_values)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_export_system_configuration_uri(self):
        oem = self.manager.get_oem_extension('Dell')

        self.assertEqual(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ExportSystemConfiguration',
            oem.export_system_configuration_uri)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test__export_system_configuration(self):
        oem = self.manager.get_oem_extension('Dell')
        oem._export_system_configuration(
            target=mgr_cons.EXPORT_TARGET_ALL)

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ExportSystemConfiguration', data={'ShareParameters':
                                                {'Target': 'ALL'},
                                                'ExportFormat': 'JSON',
                                                'ExportUse': 'Default',
                                                'IncludeInExport': 'Default'})

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test__export_system_configuration_nondefault(self):
        oem = self.manager.get_oem_extension('Dell')
        include_in_export = mgr_cons.INCLUDE_EXPORT_READ_ONLY_PASSWORD_HASHES
        oem._export_system_configuration(
            target=mgr_cons.EXPORT_TARGET_RAID,
            export_use=mgr_cons.EXPORT_USE_CLONE,
            include_in_export=include_in_export)

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ExportSystemConfiguration', data={'ShareParameters':
                                                {'Target': 'RAID'},
                                                'ExportFormat': 'JSON',
                                                'ExportUse': 'Clone',
                                                'IncludeInExport':
                                                    'IncludeReadOnly,Include'
                                                    'PasswordHashValues'})

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test__export_system_configuration_invalid_target(self):
        oem = self.manager.get_oem_extension('Dell')
        target = "xyz"
        self.assertRaises(sushy.exceptions.InvalidParameterValueError,
                          oem._export_system_configuration, target)

    def test__export_system_configuration_invalid_export_use(self):
        oem = self.manager.get_oem_extension('Dell')
        self.assertRaises(sushy.exceptions.InvalidParameterValueError,
                          oem._export_system_configuration, "RAID",
                          export_use="ABC")

    def test__export_system_configuration_invalid_include_in_export(self):
        oem = self.manager.get_oem_extension('Dell')
        self.assertRaises(sushy.exceptions.InvalidParameterValueError,
                          oem._export_system_configuration, "RAID",
                          include_in_export="ABC")

    def test__export_system_configuration_invalid_include_in_export_part(self):
        oem = self.manager.get_oem_extension('Dell')
        export_action = ('OemManager.v1_0_0'
                         '#OemManager.ExportSystemConfiguration')
        # Remove `IncludePasswordHashValues` from allowed values
        oem.json['Actions']['Oem'][export_action]['IncludeInExport@Redfish.'
                                                  'AllowableValues'] =\
            ['Default', 'IncludeReadOnly']
        oem.refresh()
        oem = self.manager.get_oem_extension('Dell')
        include_in_export = mgr_cons.INCLUDE_EXPORT_READ_ONLY_PASSWORD_HASHES
        self.assertRaises(sushy.exceptions.InvalidParameterValueError,
                          oem._export_system_configuration, "RAID",
                          include_in_export=include_in_export)

    def test__export_system_configuration_include_in_export_legacy(
            self):
        oem = self.manager.get_oem_extension('Dell')
        export_action = ('OemManager.v1_0_0'
                         '#OemManager.ExportSystemConfiguration')
        # Add `IncludeReadOnly,IncludePasswordHashValues` to allowed values
        oem.json['Actions']['Oem'][export_action]['IncludeInExport@Redfish.'
                                                  'AllowableValues'] =\
            ['Default', 'IncludeReadOnly', 'IncludePasswordHashValues',
             'IncludeReadOnly,IncludePasswordHashValues']
        oem.refresh()

        include_in_export = mgr_cons.INCLUDE_EXPORT_READ_ONLY_PASSWORD_HASHES
        oem._export_system_configuration(
            target=mgr_cons.EXPORT_TARGET_RAID,
            export_use=mgr_cons.EXPORT_USE_CLONE,
            include_in_export=include_in_export)

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ExportSystemConfiguration', data={'ShareParameters':
                                                {'Target': 'RAID'},
                                                'ExportFormat': 'JSON',
                                                'ExportUse': 'Clone',
                                                'IncludeInExport':
                                                    'IncludeReadOnly,Include'
                                                    'PasswordHashValues'})

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_allowed_export_use_values(self):
        oem = self.manager.get_oem_extension('Dell')
        expected_values = {mgr_cons.EXPORT_USE_DEFAULT,
                           mgr_cons.EXPORT_USE_CLONE,
                           mgr_cons.EXPORT_USE_REPLACE}
        allowed_values = oem.get_allowed_export_use_values()
        self.assertIsInstance(allowed_values, set)
        self.assertEqual(expected_values, allowed_values)

    @mock.patch.object(oem_manager, 'LOG', autospec=True)
    def test_get_allowed_export_use_values_missing(self, mock_log):
        oem = self.manager.get_oem_extension('Dell')
        export_action = ('OemManager.v1_0_0'
                         '#OemManager.ExportSystemConfiguration')
        oem.json['Actions']['Oem'][export_action].pop(
            'ExportUse@Redfish.AllowableValues')
        oem.refresh()
        expected_values = {mgr_cons.EXPORT_USE_DEFAULT,
                           mgr_cons.EXPORT_USE_CLONE,
                           mgr_cons.EXPORT_USE_REPLACE}
        allowed_values = oem.get_allowed_export_use_values()
        self.assertIsInstance(allowed_values, set)
        self.assertEqual(expected_values, allowed_values)
        mock_log.warning.assert_called_once()

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_allowed_include_in_export_values(self):
        oem = self.manager.get_oem_extension('Dell')
        expected_values = {mgr_cons.INCLUDE_EXPORT_DEFAULT,
                           mgr_cons.INCLUDE_EXPORT_READ_ONLY,
                           mgr_cons.INCLUDE_EXPORT_PASSWORD_HASHES}
        allowed_values = oem.get_allowed_include_in_export_values()
        self.assertIsInstance(allowed_values, set)
        self.assertEqual(expected_values, allowed_values)

    @mock.patch.object(oem_manager, 'LOG', autospec=True)
    def test_get_allowed_include_in_export_values_missing(self, mock_log):
        oem = self.manager.get_oem_extension('Dell')
        export_action = ('OemManager.v1_0_0'
                         '#OemManager.ExportSystemConfiguration')
        oem.json['Actions']['Oem'][export_action].pop(
            'IncludeInExport@Redfish.AllowableValues')
        oem.refresh()
        expected_values = {mgr_cons.INCLUDE_EXPORT_DEFAULT,
                           mgr_cons.INCLUDE_EXPORT_READ_ONLY,
                           mgr_cons.INCLUDE_EXPORT_PASSWORD_HASHES,
                           mgr_cons.INCLUDE_EXPORT_READ_ONLY_PASSWORD_HASHES}
        allowed_values = oem.get_allowed_include_in_export_values()
        self.assertIsInstance(allowed_values, set)
        self.assertEqual(expected_values, allowed_values)
        mock_log.warning.assert_called_once()

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_export_system_configuration(self):
        oem = self.manager.get_oem_extension('Dell')
        oem._export_system_configuration = mock.Mock()
        mock_response = mock.Mock()
        oem._export_system_configuration.return_value = mock_response

        response = oem.export_system_configuration()

        self.assertEqual(mock_response, response)
        oem._export_system_configuration.assert_called_once_with(
            mgr_cons.EXPORT_TARGET_ALL,
            export_use=mgr_cons.EXPORT_USE_CLONE,
            include_in_export=mgr_cons.INCLUDE_EXPORT_PASSWORD_HASHES)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_pxe_port_macs_bios(self):
        oem = self.manager.get_oem_extension('Dell')
        oem._export_system_configuration = mock.Mock()
        with open('sushy_oem_idrac/tests/unit/json_samples/'
                  'export_configuration_nic_bios.json') as f:
            mock_response = oem._export_system_configuration.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200
        ethernet_interfaces_mac = {'NIC.Integrated.1-4-1': '68:05:CA:AF:AA:C9',
                                   'NIC.Slot.7-2-1': '3C:FD:FE:CD:67:31',
                                   'NIC.Slot.7-1-1': '3C:FD:FE:CD:67:30',
                                   'NIC.Integrated.1-2-1': '68:05:CA:AF:AA:C7',
                                   'NIC.Integrated.1-3-1': '68:05:CA:AF:AA:C8',
                                   'NIC.Integrated.1-1-1': '68:05:CA:AF:AA:C6'}

        self.assertEqual(["68:05:CA:AF:AA:C8"],
                         oem.get_pxe_port_macs_bios(ethernet_interfaces_mac))

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_pxe_port_macs_bios_invalid_system_config_tag(self):
        oem = self.manager.get_oem_extension('Dell')
        oem._export_system_configuration = mock.Mock()
        mock_response = oem._export_system_configuration.return_value
        mock_response.json.return_value = {'Model': 'PowerEdge R7525'}
        mock_response.status_code = 200
        ethernet_interfaces_mac = {'NIC.Integrated.1-4-1': '68:05:CA:AF:AA:C9',
                                   'NIC.Slot.7-2-1': '3C:FD:FE:CD:67:31',
                                   'NIC.Slot.7-1-1': '3C:FD:FE:CD:67:30',
                                   'NIC.Integrated.1-2-1': '68:05:CA:AF:AA:C7',
                                   'NIC.Integrated.1-3-1': '68:05:CA:AF:AA:C8',
                                   'NIC.Integrated.1-1-1': '68:05:CA:AF:AA:C6'}

        self.assertRaises(sushy.exceptions.ExtensionError,
                          oem.get_pxe_port_macs_bios, ethernet_interfaces_mac)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_get_pxe_port_macs_bios_invalid_response(self):
        oem = self.manager.get_oem_extension('Dell')
        oem._export_system_configuration = mock.Mock()
        mock_response = oem._export_system_configuration.return_value
        mock_response.status_code = 204
        ethernet_interfaces_mac = {'NIC.Integrated.1-4-1': '68:05:CA:AF:AA:C9',
                                   'NIC.Slot.7-2-1': '3C:FD:FE:CD:67:31',
                                   'NIC.Slot.7-1-1': '3C:FD:FE:CD:67:30',
                                   'NIC.Integrated.1-2-1': '68:05:CA:AF:AA:C7',
                                   'NIC.Integrated.1-3-1': '68:05:CA:AF:AA:C8',
                                   'NIC.Integrated.1-1-1': '68:05:CA:AF:AA:C6'}

        self.assertRaises(sushy.exceptions.ExtensionError,
                          oem.get_pxe_port_macs_bios, ethernet_interfaces_mac)

    def test_idrac_card_service(self):
        oem = self.manager.get_oem_extension('Dell')
        with open('sushy_oem_idrac/tests/unit/json_samples/'
                  'idrac_card_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200
        idrac_card_service = oem.idrac_card_service
        self.assertEqual(
            '/redfish/v1/Dell/Managers/iDRAC.Embedded.1/DelliDRACCardService',
            idrac_card_service.path)
        self.assertIsInstance(idrac_card_service,
                              idrac_card.DelliDRACCardService)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_lifecycle_service(self):
        oem = self.manager.get_oem_extension('Dell')
        with open('sushy_oem_idrac/tests/unit/json_samples/'
                  'lifecycle_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200
        lifecycle_service = oem.lifecycle_service
        self.assertEqual(
            '/redfish/v1/Dell/Managers/iDRAC.Embedded.1/DellLCService',
            lifecycle_service.path)
        self.assertIsInstance(lifecycle_service,
                              lifecycle.DellLCService)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_job_service(self):
        oem = self.manager.get_oem_extension('Dell')
        with open('sushy_oem_idrac/tests/unit/json_samples/'
                  'job_service.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200
        job_service = oem.job_service
        self.assertEqual(
            '/redfish/v1/Dell/Managers/iDRAC.Embedded.1/DellJobService',
            job_service.path)
        self.assertIsInstance(job_service,
                              job.DellJobService)

    @mock.patch('sushy.resources.oem.common._global_extn_mgrs_by_resource', {})
    def test_job_collection(self):
        oem = self.manager.get_oem_extension('Dell')
        with open('sushy_oem_idrac/tests/unit/json_samples/'
                  'job_collection_expanded.json') as f:
            mock_response = self.conn.get.return_value
            mock_response.json.return_value = json.load(f)
            mock_response.status_code = 200
        job_collection = oem.job_collection
        self.assertEqual(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Jobs',
            job_collection.path)
        self.assertIsInstance(job_collection,
                              jc.DellJobCollection)

    def test_get_allowed_import_shutdown_type_values(self):
        oem = self.manager.get_oem_extension('Dell')
        expected_values = {mgr_cons.IMPORT_SHUTDOWN_GRACEFUL,
                           mgr_cons.IMPORT_SHUTDOWN_FORCED,
                           mgr_cons.IMPORT_SHUTDOWN_NO_REBOOT}
        allowed_values = oem.get_allowed_import_shutdown_type_values()
        self.assertIsInstance(allowed_values, set)
        self.assertEqual(expected_values, allowed_values)

    @mock.patch.object(oem_manager, 'LOG', autospec=True)
    def test_get_allowed_import_shutdown_type_values_missing(self, mock_log):
        oem = self.manager.get_oem_extension('Dell')
        import_action = ('OemManager.v1_0_0'
                         '#OemManager.ImportSystemConfiguration')
        oem.json['Actions']['Oem'][import_action].pop(
            'ShutdownType@Redfish.AllowableValues')
        oem.refresh()
        expected_values = {mgr_cons.IMPORT_SHUTDOWN_GRACEFUL,
                           mgr_cons.IMPORT_SHUTDOWN_FORCED,
                           mgr_cons.IMPORT_SHUTDOWN_NO_REBOOT}
        allowed_values = oem.get_allowed_import_shutdown_type_values()
        self.assertIsInstance(allowed_values, set)
        self.assertEqual(expected_values, allowed_values)
        mock_log.warning.assert_called_once()

    def test_import_system_configuration(self):
        oem = self.manager.get_oem_extension('Dell')

        result = oem.import_system_configuration('{"key": "value"}')

        self.conn.post.assert_called_once_with(
            '/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager'
            '.ImportSystemConfiguration', data={'ShareParameters':
                                                {'Target': 'ALL'},
                                                'ImportBuffer':
                                                '{"key": "value"}',
                                                'ShutdownType': 'NoReboot'})
        self.assertIsInstance(result, TaskMonitor)
        self.assertEqual('/redfish/v1/TaskService/Tasks/JID_905749031119',
                         result.task_monitor_uri)

    def test_reset_idrac_with_wait_true(self):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager.idrac_card_service.reset_idrac = mock.Mock()
        oem_manager._conn._url = "https://1.2.3.4"
        oem_manager._wait_for_idrac = mock.Mock()
        oem_manager._wait_until_idrac_is_ready = mock.Mock()
        oem_manager.reset_idrac(wait=True)
        oem_manager.idrac_card_service.reset_idrac.assert_called()
        oem_manager._wait_for_idrac.assert_called_with('1.2.3.4', 60)
        oem_manager._wait_until_idrac_is_ready.assert_called_with(
            '1.2.3.4', 96, 10)

    def test_reset_idrac_with_wait_false(self):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager.idrac_card_service.reset_idrac = mock.Mock()
        oem_manager._wait_for_idrac = mock.Mock()
        oem_manager._wait_until_idrac_is_ready = mock.Mock()
        oem_manager.reset_idrac(wait=False)
        oem_manager.idrac_card_service.reset_idrac.assert_called()
        oem_manager._wait_for_idrac.assert_not_called()
        oem_manager._wait_until_idrac_is_ready.assert_not_called()

    def test__wait_until_idrac_is_ready(self):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager.lifecycle_service.is_idrac_ready = mock.Mock()
        oem_manager.lifecycle_service.is_idrac_ready.side_effect = \
            [False, True]
        oem_manager._wait_until_idrac_is_ready('1.2.3.4', 96, 10)
        oem_manager.lifecycle_service.is_idrac_ready.assert_called_with()

    @mock.patch('time.sleep', autospec=True)
    def test__wait_until_idrac_is_ready_with_timeout(self, mock_time_sleep):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager.lifecycle_service.is_idrac_ready = mock.Mock()
        oem_manager.lifecycle_service.is_idrac_ready.return_value = False
        self.assertRaises(sushy.exceptions.ExtensionError,
                          oem_manager._wait_until_idrac_is_ready,
                          '1.2.3.4', 96, 10)

    @mock.patch('time.sleep', autospec=True)
    def test__wait_for_idrac_with_state_reached(self, mock_time_sleep):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager._wait_for_idrac_state = mock.Mock()
        oem_manager._wait_for_idrac_state.return_value = True
        oem_manager._wait_for_idrac('1.2.3.4', 30)
        oem_manager._wait_for_idrac_state.assert_called_with(
            '1.2.3.4', alive=True, ping_count=3, retries=24)
        oem_manager._wait_for_idrac_state.assert_any_call(
            '1.2.3.4', alive=False, ping_count=2, retries=24)
        self.assertEqual(2, oem_manager._wait_for_idrac_state.call_count)

    @mock.patch('time.sleep', autospec=True)
    def test__wait_for_idrac_with_first_state_not_reached(self,
                                                          mock_time_sleep):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager._wait_for_idrac_state = mock.Mock()
        oem_manager._wait_for_idrac_state.return_value = False
        self.assertRaises(sushy.exceptions.ExtensionError,
                          oem_manager._wait_for_idrac, '1.2.3.4', 30)

    @mock.patch('time.sleep', autospec=True)
    def test__wait_for_idrac_with_second_state_not_reached(self,
                                                           mock_time_sleep):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager._wait_for_idrac_state = mock.Mock()
        oem_manager._wait_for_idrac_state.side_effect = [True, False]
        self.assertRaises(sushy.exceptions.ExtensionError,
                          oem_manager._wait_for_idrac, '1.2.3.4', 30)

    @mock.patch('time.sleep', autospec=True)
    def test__wait_for_idrac_state_with_pingable(self, mock_time_sleep):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager._ping_host = mock.Mock()
        oem_manager._ping_host.return_value = True
        response = oem_manager._wait_for_idrac_state('1.2.3.4')
        self.assertEqual(True, response)
        self.assertEqual(3, oem_manager._ping_host.call_count)

    @mock.patch('time.sleep', autospec=True)
    def test__wait_for_idrac_state_without_pingable(self, mock_time_sleep):
        oem_manager = self.manager.get_oem_extension('Dell')
        oem_manager._ping_host = mock.Mock()
        oem_manager._ping_host.return_value = False
        response = oem_manager._wait_for_idrac_state('1.2.3.4')
        self.assertEqual(False, response)
        self.assertEqual(24, oem_manager._ping_host.call_count)

    @mock.patch('subprocess.call', autospec=True)
    def test__ping_host_alive(self, mock_call):
        oem_manager = self.manager.get_oem_extension('Dell')
        mock_call.return_value = 0

        result = oem_manager._ping_host('1.2.3.4')

        self.assertTrue(result)
        mock_call.assert_called_with(["ping", "-c", "1", '1.2.3.4'])

    @mock.patch('subprocess.call', autospec=True)
    def test__ping_host_not_alive(self, mock_call):
        oem_manager = self.manager.get_oem_extension('Dell')
        mock_call.return_value = 1

        result = oem_manager._ping_host('1.2.3.4')

        self.assertFalse(result)
        mock_call.assert_called_with(["ping", "-c", "1", '1.2.3.4'])
