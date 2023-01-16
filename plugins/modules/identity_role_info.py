#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Sagi Shnaidman <sshnaidm@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: identity_role_info
short_description: Retrieve information about roles
author: OpenStack Ansible SIG
description:
  - Get information about identity roles in Openstack
options:
  domain_id:
    description:
      - Domain ID which owns the role
    type: str
    required: false
  name:
    description:
      - Name or ID of the role
    type: str
    required: false
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

RETURN = '''
roles:
  description: List of identity roles
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Unique ID for the role
      returned: success
      type: str
    name:
      description: Unique role name, within the owning domain.
      returned: success
      type: str
    description:
      description: User-facing description of the role.
      returned: success
      type: str
    domain_id:
      description: References the domain ID which owns the role.
      returned: success
      type: str
    links:
      description: The links for the service resources
      returned: success
      type: dict
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
        domain_id=dict(),
        name=dict(),
    )

    module_kwargs = dict(
        supports_check_mode=True,
    )

    def run(self):
        params = {
            'domain_id': self.params['domain_id'],
            'name_or_id': self.params['name'],
        }
        params = {k: v for k, v in params.items() if v is not None}

        roles = [role.to_dict(computed=False) for role in self.conn.search_roles(**params)]
        self.exit_json(changed=False, roles=roles)


def main():
    module = IdentityRoleInfoModule()
    module()


if __name__ == '__main__':
    main()
