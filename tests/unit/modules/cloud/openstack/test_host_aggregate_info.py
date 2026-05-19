import unittest
from unittest import mock

from ansible_collections.openstack.cloud.plugins.modules import host_aggregate_info
from ansible_collections.openstack.cloud.tests.unit.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    set_module_args,
)


class FakeAggregate(dict):

    def to_dict(self, computed=False):
        return dict(self)


FAKE_AGGREGATE = FakeAggregate(
    id=7,
    uuid='583bf5e7-b228-4850-ad3e-9a0b7aa6c8da',
    name='dc1-a1',
    availability_zone='dc1-a1',
    hosts=['o3080-r01u07-1'],
    metadata={'availability_zone': 'dc1-a1'},
    created_at='2026-05-16T23:46:45.000000',
    updated_at=None,
    deleted_at=None,
    is_deleted=False,
)


class FakeSDK(object):
    class exceptions:
        class OpenStackCloudException(Exception):
            pass


class TestHostAggregateInfo(ModuleTestCase):

    def _run_module(self, module_args, compute):
        set_module_args(module_args)
        conn = mock.Mock()
        conn.compute = compute
        with mock.patch.object(
            host_aggregate_info.ComputeHostAggregateInfoModule,
            'openstack_cloud_from_module',
            return_value=(FakeSDK(), conn),
        ):
            host_aggregate_info.main()

    def _new_compute(self):
        compute = mock.Mock()
        compute.aggregates.return_value = [FAKE_AGGREGATE]
        compute.find_aggregate.return_value = FAKE_AGGREGATE
        return compute

    def test_list_all_aggregates(self):
        compute = self._new_compute()

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({'name': None}, compute)

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        self.assertEqual(1, len(result['aggregates']))
        self.assertEqual('dc1-a1', result['aggregates'][0]['name'])
        compute.aggregates.assert_called_once_with()
        compute.find_aggregate.assert_not_called()

    def test_find_aggregate_by_name(self):
        compute = self._new_compute()

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({'name': 'dc1-a1'}, compute)

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        self.assertEqual(1, len(result['aggregates']))
        self.assertEqual('dc1-a1', result['aggregates'][0]['name'])
        compute.find_aggregate.assert_called_once_with('dc1-a1')
        compute.aggregates.assert_not_called()

    def test_find_aggregate_by_name_not_found(self):
        compute = self._new_compute()
        compute.find_aggregate.return_value = None

        with self.assertRaises(AnsibleExitJson) as ex:
            self._run_module({'name': 'nonexistent'}, compute)

        result = ex.exception.args[0]
        self.assertFalse(result['changed'])
        self.assertEqual([], result['aggregates'])
        compute.find_aggregate.assert_called_once_with('nonexistent')


if __name__ == '__main__':
    unittest.main()
