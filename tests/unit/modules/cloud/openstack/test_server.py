import collections
import inspect
import pytest
from unittest import mock
import yaml

from ansible.module_utils.six import string_types
from ansible_collections.openstack.cloud.plugins.modules import server as os_server


class AnsibleFail(Exception):
    pass


class AnsibleExit(Exception):
    pass


class FakeSDK(object):
    class exceptions(object):
        class OpenStackCloudException(Exception):
            pass

        class ResourceNotFound(OpenStackCloudException):
            pass


class HelperServerModule(os_server.ServerModule):
    def __init__(self, params, conn, sdk):
        self.params = {}
        for k, v in self.argument_spec.items():
            if 'default' in v:
                self.params[k] = v['default']
            else:
                self.params[k] = None
        self.params.update(params)
        if ('floating_ips' in params or 'floating_ip_pools' in params) and 'auto_ip' not in params:
            self.params['auto_ip'] = False
        self.params = collections.defaultdict(str, self.params)

        self.conn = conn
        self.sdk = sdk
        self.module_name = 'server'
        self.check_mode = False
        self.results = {'changed': False}
        self.ansible = mock.MagicMock()
        self.ansible.check_mode = False
        self.ansible.exit_json.side_effect = AnsibleExit
        self.ansible.fail_json.side_effect = AnsibleFail
        self.exit_json = self.ansible.exit_json
        self.fail_json = self.ansible.fail_json


def params_from_doc(func):
    '''This function extracts the docstring from the specified function,
    parses it as a YAML document, and returns parameters for the openstack.cloud.server
    module.'''

    doc = inspect.getdoc(func)
    cfg = yaml.safe_load(doc)

    for task in cfg:
        for module, params in task.items():
            for k, v in params.items():
                if k in ['nics'] and isinstance(v, string_types):
                    params[k] = [v]
        task[module] = collections.defaultdict(str,
                                               params)

    return cfg[0]['openstack.cloud.server']


class FakeCloud(object):
    ports = [
        {'name': 'port1', 'id': '1234'},
        {'name': 'port2', 'id': '4321'},
    ]

    networks = [
        {'name': 'network1', 'id': '5678'},
        {'name': 'network2', 'id': '8765'},
    ]

    images = [
        {'name': 'cirros', 'id': '1'},
        {'name': 'fedora', 'id': '2'},
    ]

    flavors = [
        {'name': 'm1.small', 'id': '1', 'flavor_ram': 1024},
        {'name': 'm1.tiny', 'id': '2', 'flavor_ram': 512},
    ]

    def _find(self, source, name):
        for item in source:
            if item['name'] == name or item['id'] == name:
                return item

    def get_image_id(self, name, exclude=None):
        image = self._find(self.images, name)
        if image:
            return image['id']

    def get_flavor(self, name):
        return self._find(self.flavors, name)

    def get_flavor_by_ram(self, ram, include=None):
        for flavor in self.flavors:
            if flavor['ram'] >= ram and (include is None or include in
                                         flavor['name']):
                return flavor

    def get_port(self, name):
        return self._find(self.ports, name)

    def get_network(self, name):
        return self._find(self.networks, name)

    def get_openstack_vars(self, server):
        return server

    create_server = mock.MagicMock()


class TestNetworkArgs(object):
    '''This class exercises the _network_args function of the
    openstack.cloud.server module.  For each test, we parse the YAML document
    contained in the docstring to retrieve the module parameters for the
    test.'''

    def setup_method(self, method):
        self.cloud = FakeCloud()
        self.cloud.network = mock.MagicMock()

        def find_network(name, ignore_missing=False):
            net = self.cloud.get_network(name)
            if net:
                return mock.MagicMock(id=net['id'])
            raise Exception("Network not found")

        def find_port(name, ignore_missing=False):
            port = self.cloud.get_port(name)
            if port:
                return mock.MagicMock(id=port['id'])
            raise Exception("Port not found")

        self.cloud.network.find_network.side_effect = find_network
        self.cloud.network.find_port.side_effect = find_port

        self.params = params_from_doc(method)
        self.module = HelperServerModule(self.params, self.cloud, FakeSDK())

    def test_nics_string_net_id(self):
        '''
        - openstack.cloud.server:
            nics: net-id=1234
        '''
        args = self.module._parse_nics()
        assert args[0]['net-id'] == '1234'

    def test_nics_string_net_id_list(self):
        '''
        - openstack.cloud.server:
            nics: net-id=1234,net-id=4321
        '''
        args = self.module._parse_nics()
        assert args[0]['net-id'] == '1234'
        assert args[1]['net-id'] == '4321'

    def test_nics_string_port_id(self):
        '''
        - openstack.cloud.server:
            nics: port-id=1234
        '''
        args = self.module._parse_nics()
        assert args[0]['port-id'] == '1234'

    def test_nics_string_net_name(self):
        '''
        - openstack.cloud.server:
            nics: net-name=network1
        '''
        args = self.module._parse_nics()
        assert args[0]['net-id'] == '5678'

    def test_nics_string_port_name(self):
        '''
        - openstack.cloud.server:
            nics: port-name=port1
        '''
        args = self.module._parse_nics()
        assert args[0]['port-id'] == '1234'

    def test_nics_structured_net_id(self):
        '''
        - openstack.cloud.server:
            nics:
                - net-id: '1234'
        '''
        args = self.module._parse_nics()
        assert args[0]['net-id'] == '1234'

    def test_nics_structured_mixed(self):
        '''
        - openstack.cloud.server:
            nics:
                - net-id: '1234'
                - port-name: port1
                - 'net-name=network1,port-id=4321'
        '''
        args = self.module._parse_nics()
        assert args[0]['net-id'] == '1234'
        assert args[1]['port-id'] == '1234'
        assert args[2]['net-id'] == '5678'
        assert args[3]['port-id'] == '4321'


class TestCreateServer(object):
    def setup_method(self, method):
        self.cloud = FakeCloud()
        self.cloud.compute = mock.MagicMock()
        self.cloud.compute.find_server.return_value = None
        self.cloud.compute.get_server.return_value = mock.MagicMock()
        self.cloud.compute.get_server.return_value.to_dict.return_value = {'id': '1234'}

        def find_flavor(name_or_id, ignore_missing=True):
            flavor = self.cloud.get_flavor(name_or_id)
            if flavor:
                return mock.MagicMock(id=flavor['id'])
            if not ignore_missing:
                raise FakeSDK.exceptions.ResourceNotFound("Could not find flavor {0}".format(name_or_id))
            return None
        self.cloud.compute.find_flavor.side_effect = find_flavor

        self.cloud.network = mock.MagicMock()

        def find_network(name, ignore_missing=False):
            net = self.cloud.get_network(name)
            if net:
                return mock.MagicMock(id=net['id'])
            raise Exception("Network not found")
        self.cloud.network.find_network.side_effect = find_network

        self.params = params_from_doc(method)
        self.module = HelperServerModule(self.params, self.cloud, FakeSDK())

        self.meta = mock.MagicMock()
        self.meta.gett_hostvars_from_server.return_value = {
            'id': '1234'
        }
        os_server.meta = self.meta

    def test_create_server(self):
        '''
        - openstack.cloud.server:
            image: cirros
            flavor: m1.tiny
            nics:
              - net-name: network1
            meta:
              - key: value
        '''
        with pytest.raises(AnsibleExit):
            self.module()

        assert self.cloud.create_server.call_count == 1
        assert self.cloud.create_server.call_args[1]['image'] == self.cloud.get_image_id('cirros')
        assert self.cloud.create_server.call_args[1]['flavor'] == self.cloud.get_flavor('m1.tiny')['id']
        assert self.cloud.create_server.call_args[1]['nics'][0]['net-id'] == self.cloud.get_network('network1')['id']

    def test_create_server_bad_flavor(self):
        '''
        - openstack.cloud.server:
            image: cirros
            flavor: missing_flavor
            nics:
              - net-name: network1
        '''
        with pytest.raises(AnsibleFail):
            self.module()

        assert 'missing_flavor' in self.module.fail_json.call_args[1]['msg']

    def test_create_server_bad_nic(self):
        '''
        - openstack.cloud.server:
            image: cirros
            flavor: m1.tiny
            nics:
              - net-name: missing_network
        '''
        def find_network_fail(name, ignore_missing=False):
            raise FakeSDK.exceptions.ResourceNotFound("missing_network")
        self.cloud.network.find_network.side_effect = find_network_fail

        with pytest.raises(AnsibleFail):
            self.module()

        assert 'missing_network' in self.module.fail_json.call_args[1]['msg']

    def test_create_server_auto_ip_wait(self):
        '''
        - openstack.cloud.server:
            image: cirros
            auto_ip: true
            wait: false
            nics:
              - net-name: network1
        '''
        with pytest.raises(AnsibleFail):
            self.module()

        assert 'auto_ip' in self.module.fail_json.call_args[1]['msg']

    def test_create_server_floating_ips_wait(self):
        '''
        - openstack.cloud.server:
            image: cirros
            floating_ips: ['0.0.0.0']
            wait: false
            nics:
              - net-name: network1
        '''
        with pytest.raises(AnsibleFail):
            self.module()

        assert 'floating_ips' in self.module.fail_json.call_args[1]['msg']

    def test_create_server_floating_ip_pools_wait(self):
        '''
        - openstack.cloud.server:
            image: cirros
            floating_ip_pools: ['name-of-pool']
            wait: false
            nics:
              - net-name: network1
        '''
        with pytest.raises(AnsibleFail):
            self.module()

        assert 'floating_ip_pools' in self.module.fail_json.call_args[1]['msg']
