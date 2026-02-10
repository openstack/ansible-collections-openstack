#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026 OpenStack Ansible SIG
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
module: baremetal_port_group
short_description: Create/Delete Bare Metal port group resources from OpenStack
author: OpenStack Ansible SIG
description:
    - Create, update and remove Bare Metal port groups from OpenStack.
options:
    id:
      description:
        - ID of the port group.
        - Will be auto-generated if not specified.
      type: str
      aliases: ['uuid']
    name:
      description:
        - Name of the port group.
      type: str
    node:
      description:
        - ID or Name of the node this resource belongs to.
        - Required when creating a new port group.
      type: str
    address:
      description:
        - Physical hardware address of this port group, typically the hardware
          MAC address.
      type: str
    extra:
      description:
        - A set of one or more arbitrary metadata key and value pairs.
      type: dict
    standalone_ports_supported:
      description:
        - Whether the port group supports ports that are not members of this
          port group.
      type: bool
    mode:
      description:
        - The port group mode.
      type: str
    properties:
      description:
        - Key/value properties for the port group.
      type: dict
    state:
      description:
        - Indicates desired state of the resource.
      choices: ['present', 'absent']
      default: present
      type: str
extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = r'''
- name: Create Bare Metal port group
  openstack.cloud.baremetal_port_group:
    cloud: devstack
    state: present
    name: bond0
    node: bm-0
    address: fa:16:3e:aa:aa:aa
    mode: '802.3ad'
    standalone_ports_supported: true
  register: result

- name: Update Bare Metal port group
  openstack.cloud.baremetal_port_group:
    cloud: devstack
    state: present
    id: 1a85ebca-22bf-42eb-ad9e-f640789b8098
    mode: 'active-backup'
    properties:
      miimon: '100'
  register: result

- name: Delete Bare Metal port group
  openstack.cloud.baremetal_port_group:
    cloud: devstack
    state: absent
    id: 1a85ebca-22bf-42eb-ad9e-f640789b8098
  register: result
'''

RETURN = r'''
port_group:
    description: A port group dictionary, subset of the dictionary keys listed
                 below may be returned, depending on your cloud provider.
    returned: success
    type: dict
    contains:
        address:
            description: Physical hardware address of the port group.
            returned: success
            type: str
        created_at:
            description: Bare Metal port group created at timestamp.
            returned: success
            type: str
        extra:
            description: A set of one or more arbitrary metadata key and value
                         pairs.
            returned: success
            type: dict
        id:
            description: The UUID for the Bare Metal port group resource.
            returned: success
            type: str
        links:
            description: A list of relative links, including the self and
                         bookmark links.
            returned: success
            type: list
        mode:
            description: The port group mode.
            returned: success
            type: str
        name:
            description: Bare Metal port group name.
            returned: success
            type: str
        node_id:
            description: UUID of the Bare Metal node this resource belongs to.
            returned: success
            type: str
        properties:
            description: Key/value properties for this port group.
            returned: success
            type: dict
        standalone_ports_supported:
            description: Whether standalone ports are supported.
            returned: success
            type: bool
        updated_at:
            description: Bare Metal port group updated at timestamp.
            returned: success
            type: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule
)


class BaremetalPortGroupModule(OpenStackModule):
    argument_spec = dict(
        id=dict(aliases=['uuid']),
        name=dict(),
        node=dict(),
        address=dict(),
        extra=dict(type='dict'),
        standalone_ports_supported=dict(type='bool'),
        mode=dict(),
        properties=dict(type='dict'),
        state=dict(default='present', choices=['present', 'absent']),
    )

    module_kwargs = dict(
        required_one_of=[
            ('id', 'name'),
        ],
        supports_check_mode=True,
    )

    def _find_port_group(self):
        id_or_name = self.params['id'] if self.params['id'] else self.params['name']
        if not id_or_name:
            return None

        try:
            return self.conn.baremetal.find_port_group(id_or_name)
        except self.sdk.exceptions.ResourceNotFound:
            return None

    def _build_create_attrs(self):
        attrs = {}

        for key in ['id', 'name', 'address', 'extra',
                    'standalone_ports_supported', 'mode', 'properties']:
            if self.params[key] is not None:
                attrs[key] = self.params[key]

        node_name_or_id = self.params['node']
        if not node_name_or_id:
            self.fail_json(msg="Parameter 'node' is required when creating a new port group")

        node = self.conn.baremetal.find_node(node_name_or_id, ignore_missing=False)
        attrs['node_id'] = node['id']
        return attrs

    def _build_update_attrs(self, port_group):
        attrs = {}

        for key in ['name', 'address', 'extra',
                    'standalone_ports_supported', 'mode', 'properties']:
            if self.params[key] is not None and self.params[key] != port_group.get(key):
                attrs[key] = self.params[key]

        return attrs

    def _will_change(self, port_group, state):
        if state == 'absent':
            return bool(port_group)

        if not port_group:
            return True

        return bool(self._build_update_attrs(port_group))

    def run(self):
        state = self.params['state']
        port_group = self._find_port_group()

        if self.ansible.check_mode:
            if state == 'present' and not port_group:
                self._build_create_attrs()
            self.exit_json(changed=self._will_change(port_group, state))

        if state == 'present':
            if not port_group:
                port_group = self.conn.baremetal.create_port_group(
                    **self._build_create_attrs())
                self.exit_json(
                    changed=True,
                    port_group=port_group.to_dict(computed=False))

            update_attrs = self._build_update_attrs(port_group)
            changed = bool(update_attrs)

            if changed:
                port_group = self.conn.baremetal.update_port_group(
                    port_group['id'], **update_attrs)

            self.exit_json(
                changed=changed,
                port_group=port_group.to_dict(computed=False))

        if not port_group:
            self.exit_json(changed=False)

        self.conn.baremetal.delete_port_group(port_group['id'])
        self.exit_json(changed=True)


def main():
    module = BaremetalPortGroupModule()
    module()


if __name__ == "__main__":
    main()
