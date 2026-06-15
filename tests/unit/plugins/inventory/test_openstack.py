# -*- coding: utf-8 -*-

# Copyright 2018 Lars Kellogg-Stedman <lars@redhat.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish

import pytest

from ansible_collections.openstack.cloud.plugins.inventory.openstack import InventoryModule
from ansible.inventory.data import InventoryData
from ansible.template import Templar


config_data = {
    'plugin': 'openstack',
    'compose': {
        'composed_var': '"testvar-" + testvar',
    },
    'groups': {
        'testgroup': '"host" in inventory_hostname',
    },
    'keyed_groups':
    [{
        'prefix': 'keyed',
        'key': 'testvar',
    }]
}

hostvars = {
    'host0': {
        'inventory_hostname': 'host0',
        'testvar': '0',
    },
    'host1': {
        'inventory_hostname': 'host1',
        'testvar': '1',
    },
}


try:
    from ansible._internal._templating._engine import TrustedAsTemplate
    has_trusted = True
except ImportError:
    has_trusted = False


def tag_trusted(val):
    if not has_trusted:
        return val
    if isinstance(val, dict):
        return {k: tag_trusted(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [tag_trusted(v) for v in val]
    elif isinstance(val, str):
        return TrustedAsTemplate().tag(val)
    return val


@pytest.fixture(scope="module")
def inventory():
    inventory = InventoryModule()
    inventory._config_data = tag_trusted(config_data)
    inventory.inventory = InventoryData()
    inventory.templar = Templar(loader=None)

    for host in hostvars:
        inventory.inventory.add_host(host)

    def _set_variables(hostvars, groups):
        for host in hostvars:
            try:
                inventory._set_composite_vars(
                    inventory._config_data.get('compose'), hostvars[host], host, strict=True)
            except Exception as e:
                print("set_composite_vars error: %s" % e)
                raise
            for key in hostvars[host]:
                inventory.inventory.set_variable(host, key, hostvars[host][key])
            try:
                inventory._add_host_to_composed_groups(
                    inventory._config_data.get('groups'), hostvars[host], host, strict=True)
            except Exception as e:
                print("add_host_to_composed_groups error: %s" % e)
                raise
            try:
                inventory._add_host_to_keyed_groups(
                    inventory._config_data.get('keyed_groups'), hostvars[host], host, strict=True)
            except Exception as e:
                print("add_host_to_keyed_groups error: %s" % e)
                raise

    inventory._set_variables = _set_variables
    return inventory


def test_simple_groups(inventory):
    inventory._set_variables(hostvars, {})
    groups = inventory.inventory.get_groups_dict()
    assert 'testgroup' in groups
    assert len(groups['testgroup']) == len(hostvars)


def test_keyed_groups(inventory):
    inventory._set_variables(hostvars, {})
    assert 'keyed_0' in inventory.inventory.groups
    assert 'keyed_1' in inventory.inventory.groups


def test_composed_vars(inventory):
    inventory._set_variables(hostvars, {})

    for host in hostvars:
        assert host in inventory.inventory.hosts
        host = inventory.inventory.get_host(host)
        assert host.vars['composed_var'] == 'testvar-{testvar}'.format(**hostvars[host.name])
