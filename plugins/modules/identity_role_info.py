#!/usr/bin/python
# coding: utf-8 -*-

# Copyright (c) 2020, Sagi Shnaidman <sshnaidm@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: identity_role_info
short_description: Retrive information about roles
author: OpenStack Ansible SIG
description:
  - Get information about identity roles in Openstack
options:
  domain_id:
    description:
      - List roles in specified domain only
    type: str
    required: false
  name:
    description:
      - List role speficied by name
    type: str
    required: false

requirements:
  - "python >= 3.6"
  - "openstacksdk"

extends_documentation_fragment:
  - openstack.cloud.openstack
'''

RETURN = '''
openstack_roles:
  description: List of identity roles
  returned: always
  type: list
  elements: dict
  sample:
  - domain_id: None
    id: 19bf514fdda84f808ccee8463bd85c1a
    location:
      cloud: mycloud
      project:
        domain_id: None
        domain_name: None
        id: None
        name: None
      region_name: None
      zone: None
    name: member
    properties:

'''

EXAMPLES = '''
# Retrieve info about all roles
- openstack.cloud.identity_role_info:
    cloud: mycloud

# Retrieve info about all roles in specific domain
- openstack.cloud.identity_role_info:
    cloud: mycloud
    domain_id: some_domain_id

# Retrieve info about role 'admin'
- openstack.cloud.identity_role_info:
    cloud: mycloud
    name: admin

'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityRoleInfoModule(OpenStackModule):

    argument_spec = dict(
        domain_id=dict(type='str', required=False),
        name=dict(type='str', required=False),
    )
    module_kwargs = dict(
        supports_check_mode=True,
    )

    def run(self):
        roles = self.conn.list_roles(domain_id=self.params['domain_id'])
        # Dictionaries are supported from Train release
        roles = [item if isinstance(item, dict) else item.to_dict() for item in roles]
        # Filtering by name is supported from Wallaby release
        if self.params['name']:
            roles = [item for item in roles if self.params['name'] in (item['id'], item['name'])]
        self.results.update({'openstack_roles': roles})


def main():
    module = IdentityRoleInfoModule()
    module()


if __name__ == '__main__':
    main()
