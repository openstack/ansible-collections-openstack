
import munch

from ansible_collections.openstack.cloud.plugins.modules import routers_info
from ansible_collections.openstack.cloud.tests.unit.modules.utils import ModuleTestCase


def openstack_cloud_from_module(module, **kwargs):
    return FakeSDK(), FakeCloud()


class FakeSDK(object):
    class exceptions:
        class OpenStackCloudException(Exception):
            pass


class FakeCloud(object):

    def search_routers(self, name_or_id=None, filters=None):
        test_routers = [
            {
                "admin_state_up": True,
                "availability_zone_hints": [],
                "availability_zones": [
                    "nova"
                ],
                "created_at": "2019-12-19T20:16:18Z",
                "description": "",
                "distributed": False,
                "external_gateway_info": None,
                "flavor_id": None,
                "ha": False,
                "id": "d3f70ce4-7ab1-46a7-9bec-498c9d8a2483",
                "name": "router1",
                "project_id": "f48189aaee42429e8ed396e8b3f6a018",
                "revision_number": 14,
                "routes": [],
                "status": "ACTIVE",
                "tags": [],
                "tenant_id": "f48189aaee42429e8ed396e8b3f6a018",
                "updated_at": "2020-01-27T21:20:09Z"
            },
            {
                "admin_state_up": True,
                "availability_zone_hints": [],
                "availability_zones": [
                    "nova"
                ],
                "created_at": "2019-12-19T20:16:18Z",
                "description": "",
                "distributed": False,
                "external_gateway_info": {
                    "enable_snat": True,
                    "external_fixed_ips": [
                        {
                            "ip_address": "172.24.4.163",
                            "subnet_id": "b42b8057-5b3b-4aa3-949a-eaaee2032462"
                        },
                    ],
                    "network_id": "fd6cc0f1-ed6f-426e-bb7b-a942b12633ad"
                },
                "flavor_id": None,
                "ha": False,
                "id": "b869307c-a1f9-4956-a993-8a90fc7cc01d",
                "name": "router2",
                "project_id": "f48189aaee42429e8ed396e8b3f6a018",
                "revision_number": 6,
                "routes": [],
                "status": "ACTIVE",
                "tags": [],
                "tenant_id": "f48189aaee42429e8ed396e8b3f6a018",
                "updated_at": "2019-12-19T20:18:46Z"
            },
            {
                "admin_state_up": True,
                "availability_zone_hints": [],
                "availability_zones": [
                    "nova"
                ],
                "created_at": "2020-01-24T20:19:35Z",
                "description": "",
                "distributed": False,
                "external_gateway_info": {
                    "enable_snat": True,
                    "external_fixed_ips": [
                        {
                            "ip_address": "172.24.4.234",
                            "subnet_id": "b42b8057-5b3b-4aa3-949a-eaaee2032462"
                        },
                    ],
                    "network_id": "fd6cc0f1-ed6f-426e-bb7b-a942b12633ad"
                },
                "flavor_id": None,
                "ha": False,
                "id": "98bce30e-c912-4490-85eb-b22d650721e6",
                "name": "router3",
                "project_id": "f48189aaee42429e8ed396e8b3f6a018",
                "revision_number": 4,
                "routes": [],
                "status": "ACTIVE",
                "tags": [],
                "tenant_id": "f48189aaee42429e8ed396e8b3f6a018",
                "updated_at": "2020-01-26T10:21:31Z"
            },
        ]

        if name_or_id is not None:
            return [munch.Munch(router) for router in test_routers
                    if router["name"] == name_or_id]
        else:
            return [munch.Munch(router) for router in test_routers]


class TestRoutersInfo(ModuleTestCase):
    '''This class calls the main function of the
    openstack.cloud.routers_info module.
    '''

    def setUp(self):
        super(TestRoutersInfo, self).setUp()
        self.module = routers_info

    def module_main(self, exit_exc):
        with self.assertRaises(exit_exc) as exc:
            self.module.main()
        return exc.exception.args[0]
