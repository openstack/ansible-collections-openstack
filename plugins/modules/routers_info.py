#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2019, Bram Verschueren <verschueren.bram@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: routers_info
short_description: Retrieve information about one or more OpenStack routers.
author: OpenStack Ansible SIG
description:
    - Retrieve information about one or more routers from OpenStack.
options:
   name:
     description:
        - Name or ID of the router
     required: false
     type: str
   filters:
     description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
     required: false
     type: dict
     suboptions:
       project_id:
         description:
           - Filter the list result by the ID of the project that owns the resource.
         type: str
         aliases:
           - tenant_id
       name:
         description:
           - Filter the list result by the human-readable name of the resource.
         type: str
       description:
         description:
           - Filter the list result by the human-readable description of the resource.
         type: str
       is_admin_state_up:
         description:
           - Filter the list result by the administrative state of the resource, which is up (true) or down (false).
         type: bool
       revision_number:
         description:
           - Filter the list result by the revision number of the resource.
         type: int
       tags:
         description:
           - A list of tags to filter the list result by. Resources that match all tags in this list will be returned.
         type: list
         elements: str
requirements:
    - "python >= 3.6"
    - "openstacksdk"
extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Gather information about routers
  openstack.cloud.routers_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
  register: result

- name: Show openstack routers
  debug:
    msg: "{{ result.routers }}"

- name: Gather information about a router by name
  openstack.cloud.routers_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    name: router1
  register: result

- name: Show openstack routers
  debug:
    msg: "{{ result.routers }}"

- name: Gather information about a router with filter
  openstack.cloud.routers_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    filters:
      is_admin_state_up: True
  register: result

- name: Show openstack routers
  debug:
    msg: "{{ result.routers }}"
'''

RETURN = '''
routers:
    description: has all the openstack information about the routers
    returned: always, but can be null
    type: list
    elements: dict
    contains:
        availability_zones:
            description: Availability zones
            returned: success
            type: list
        availability_zone_hints:
            description: Availability zone hints
            returned: success
            type: list
        created_at:
            description: Date and time when the router was created
            returned: success
            type: str
        description:
            description: Description notes of the router
            returned: success
            type: str
        external_gateway_info:
            description: The external gateway information of the router.
            returned: success
            type: dict
        flavor_id:
            description: ID of the flavor of the router
            returned: success
            type: str
        id:
            description: Unique UUID.
            returned: success
            type: str
        interfaces_info:
            description: List of connected interfaces.
            returned: success
            type: list
        is_admin_state_up:
            description: Network administrative state
            returned: success
            type: bool
        is_distributed:
            description: Indicates a distributed router.
            returned: success
            type: bool
        is_ha:
            description: Indicates a highly-available router.
            returned: success
            type: bool
        name:
            description: Name given to the router.
            returned: success
            type: str
        project_id:
            description: Project id associated with this router.
            returned: success
            type: str
        revision_number:
            description: Revision number
            returned: success
            type: int
        routes:
            description: The extra routes configuration for L3 router.
            returned: success
            type: list
        status:
            description: Router status.
            returned: success
            type: str
        tags:
            description: List of tags
            returned: success
            type: list
        tenant_id:
            description: Owner tenant ID
            returned: success
            type: str
        updated_at:
            description: Date of last update on the router
            returned: success
            type: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class RouterInfoModule(OpenStackModule):

    deprecated_names = ('os_routers_info', 'openstack.cloud.os_routers_info')

    argument_spec = dict(
        name=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default={})
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        routers = self.conn.search_routers(name_or_id=self.params['name'],
                                           filters=self.params['filters'])

        routers = [r.to_dict(computed=False) for r in routers]

        # The following code replicates self.conn.list_router_interfaces()
        # but only uses a single api call per router instead of four api
        # calls as the former does.
        allowed_device_owners = ('network:router_interface',
                                 'network_router_interface_distributed',
                                 'network:ha_router_replicated_interface',
                                 'network:router_gateway')
        for router in routers:
            interfaces_info = []
            for port in self.conn.network.ports(device_id=router['id']):
                if port.device_owner not in allowed_device_owners:
                    continue
                if port.device_owner != "network:router_gateway":
                    for ip_spec in port.fixed_ips:
                        int_info = {
                            'port_id': port.id,
                            'ip_address': ip_spec.get('ip_address'),
                            'subnet_id': ip_spec.get('subnet_id')
                        }
                        interfaces_info.append(int_info)
            router['interfaces_info'] = interfaces_info

        self.exit(changed=False, routers=routers)


def main():
    module = RouterInfoModule()
    module()


if __name__ == '__main__':
    main()
