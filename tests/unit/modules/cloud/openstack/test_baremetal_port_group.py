import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


def _load_module_under_test():
    module_path = Path(__file__).resolve().parents[5] / 'plugins/modules/baremetal_port_group.py'
    spec = importlib.util.spec_from_file_location('baremetal_port_group', str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError('Cannot load baremetal_port_group module for tests')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baremetal_port_group = _load_module_under_test()


def set_module_args(args):
    if '_ansible_remote_tmp' not in args:
        args['_ansible_remote_tmp'] = '/tmp'
    if '_ansible_keep_remote_files' not in args:
        args['_ansible_keep_remote_files'] = False

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs):
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class ModuleTestCase(unittest.TestCase):
    mock_module = None
    mock_sleep = None

    def setUp(self):
        self.mock_module = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
        )
        self.mock_module.start()
        self.mock_sleep = patch('time.sleep')
        self.mock_sleep.start()
        set_module_args({})
        self.addCleanup(self.mock_module.stop)
        self.addCleanup(self.mock_sleep.stop)


class FakePortGroup(dict[str, object]):

    def to_dict(self, computed=False):
        return dict(self)


class FakeSDK(object):
    class exceptions:
        class OpenStackCloudException(Exception):
            pass

        class ResourceNotFound(Exception):
            pass


class TestBaremetalPortGroup(ModuleTestCase):
    module = baremetal_port_group

    def setUp(self):
        super(TestBaremetalPortGroup, self).setUp()
        self.module = baremetal_port_group

    def _run_module(self, module_args, baremetal):
        set_module_args(module_args)
        conn = mock.Mock()
        conn.baremetal = baremetal
        with mock.patch.object(
            baremetal_port_group.BaremetalPortGroupModule,
            'openstack_cloud_from_module',
            return_value=(FakeSDK(), conn),
        ):
            self.module.main()

    def _new_baremetal(self):
        baremetal = mock.Mock()
        baremetal.find_port_group.return_value = None
        baremetal.find_node.return_value = {'id': 'node-1'}
        return baremetal

    def test_create_port_group(self):
        baremetal = self._new_baremetal()
        baremetal.create_port_group.return_value = FakePortGroup(
            id='pg-1',
            name='bond0',
            node_id='node-1',
            address='fa:16:3e:aa:aa:aa',
            mode='active-backup',
            extra={},
            properties={},
            standalone_ports_supported=True,
            links=[],
            created_at='2026-01-01T00:00:00+00:00',
            updated_at=None,
        )

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    'id': None,
                    'name': 'bond0',
                    'node': 'node-name',
                    'address': 'fa:16:3e:aa:aa:aa',
                    'extra': {},
                    'standalone_ports_supported': True,
                    'mode': 'active-backup',
                    'properties': {},
                    'state': 'present',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        self.assertEqual('pg-1', result['port_group']['id'])
        baremetal.find_node.assert_called_once_with('node-name', ignore_missing=False)
        baremetal.create_port_group.assert_called_once_with(
            name='bond0',
            node_id='node-1',
            address='fa:16:3e:aa:aa:aa',
            extra={},
            standalone_ports_supported=True,
            mode='active-backup',
            properties={},
        )

    def test_create_port_group_without_node_fails(self):
        baremetal = self._new_baremetal()

        with self.assertRaises(AnsibleFailJson) as ex:
            self._run_module(
                {
                    'id': None,
                    'name': 'bond0',
                    'node': None,
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': None,
                    'properties': None,
                    'state': 'present',
                },
                baremetal,
            )

        self.assertIn("Parameter 'node' is required", ex.exception.args[0]['msg'])
        baremetal.create_port_group.assert_not_called()

    def test_update_port_group_when_values_changed(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.return_value = FakePortGroup(
            id='pg-1',
            name='bond0',
            node_id='node-1',
            mode='active-backup',
            address=None,
            extra={},
            properties={},
            standalone_ports_supported=True,
            links=[],
            created_at='2026-01-01T00:00:00+00:00',
            updated_at=None,
        )
        baremetal.update_port_group.return_value = FakePortGroup(
            id='pg-1',
            name='bond0',
            node_id='node-1',
            mode='802.3ad',
            address=None,
            extra={},
            properties={},
            standalone_ports_supported=True,
            links=[],
            created_at='2026-01-01T00:00:00+00:00',
            updated_at='2026-01-02T00:00:00+00:00',
        )

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    'id': 'pg-1',
                    'name': None,
                    'node': None,
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': '802.3ad',
                    'properties': None,
                    'state': 'present',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        self.assertEqual('802.3ad', result['port_group']['mode'])
        baremetal.update_port_group.assert_called_once_with('pg-1', mode='802.3ad')

    def test_present_noop_when_already_matching(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.return_value = FakePortGroup(
            id='pg-1',
            name='bond0',
            node_id='node-1',
            mode='active-backup',
            address='fa:16:3e:aa:aa:aa',
            extra={'a': 'b'},
            properties={'miimon': '100'},
            standalone_ports_supported=False,
            links=[],
            created_at='2026-01-01T00:00:00+00:00',
            updated_at=None,
        )

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    'id': 'pg-1',
                    'name': 'bond0',
                    'node': None,
                    'address': 'fa:16:3e:aa:aa:aa',
                    'extra': {'a': 'b'},
                    'standalone_ports_supported': False,
                    'mode': 'active-backup',
                    'properties': {'miimon': '100'},
                    'state': 'present',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        baremetal.update_port_group.assert_not_called()

    def test_delete_existing_port_group(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.return_value = FakePortGroup(id='pg-1', name='bond0')

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    'id': 'pg-1',
                    'name': None,
                    'node': None,
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': None,
                    'properties': None,
                    'state': 'absent',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        baremetal.delete_port_group.assert_called_once_with('pg-1')

    def test_delete_missing_port_group_is_noop(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.return_value = None

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    'id': 'pg-1',
                    'name': None,
                    'node': None,
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': None,
                    'properties': None,
                    'state': 'absent',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        baremetal.delete_port_group.assert_not_called()

    def test_check_mode_create_marks_changed(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.return_value = None

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    '_ansible_check_mode': True,
                    'id': None,
                    'name': 'bond0',
                    'node': 'node-name',
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': None,
                    'properties': None,
                    'state': 'present',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertTrue(result['changed'])
        baremetal.create_port_group.assert_not_called()
        baremetal.find_node.assert_called_once_with('node-name', ignore_missing=False)

    def test_check_mode_create_without_node_fails(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.return_value = None

        with self.assertRaises(AnsibleFailJson) as ex:
            self._run_module(
                {
                    '_ansible_check_mode': True,
                    'id': None,
                    'name': 'bond0',
                    'node': None,
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': None,
                    'properties': None,
                    'state': 'present',
                },
                baremetal,
            )

        self.assertIn("Parameter 'node' is required", ex.exception.args[0]['msg'])
        baremetal.create_port_group.assert_not_called()
        baremetal.find_node.assert_not_called()

    def test_find_port_group_resource_not_found_returns_none(self):
        baremetal = self._new_baremetal()
        baremetal.find_port_group.side_effect = FakeSDK.exceptions.ResourceNotFound()

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module(
                {
                    'id': 'pg-1',
                    'name': None,
                    'node': None,
                    'address': None,
                    'extra': None,
                    'standalone_ports_supported': None,
                    'mode': None,
                    'properties': None,
                    'state': 'absent',
                },
                baremetal,
            )

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
