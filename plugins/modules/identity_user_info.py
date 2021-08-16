#!/usr/bin/python
# Copyright (c) 2016 Hewlett-Packard Enterprise Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: identity_user_info
short_description: Retrieve information about one or more OpenStack users
author: OpenStack Ansible SIG
description:
    - Retrieve information about a one or more OpenStack users
    - This module was called C(openstack.cloud.identity_user_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(openstack.cloud.identity_user_info) module no longer returns C(ansible_facts)!
options:
   name:
     description:
        - Name or ID of the user
     type: str
   domain:
     description:
        - Name or ID of the domain containing the user if the cloud supports domains
     type: str
   filters:
     description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
     type: dict
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Gather information about previously created users
- openstack.cloud.identity_user_info:
    cloud: awesomecloud
  register: result
- debug:
    msg: "{{ result.openstack_users }}"

# Gather information about a previously created user by name
- openstack.cloud.identity_user_info:
    cloud: awesomecloud
    name: demouser
  register: result
- debug:
    msg: "{{ result.openstack_users }}"

# Gather information about a previously created user in a specific domain
- openstack.cloud.identity_user_info:
    cloud: awesomecloud
    name: demouser
    domain: admindomain
  register: result
- debug:
    msg: "{{ result.openstack_users }}"

# Gather information about a previously created user in a specific domain with filter
- openstack.cloud.identity_user_info:
    cloud: awesomecloud
    name: demouser
    domain: admindomain
    filters:
      enabled: False
  register: result
- debug:
    msg: "{{ result.openstack_users }}"
'''


RETURN = '''
openstack_users:
    description: has all the OpenStack information about users
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: str
        name:
            description: Name given to the user.
            returned: success
            type: str
        enabled:
            description: Flag to indicate if the user is enabled
            returned: success
            type: bool
        domain_id:
            description: Domain ID containing the user
            returned: success
            type: str
        default_project_id:
            description: Default project ID of the user
            returned: success
            type: str
        email:
            description: Email of the user
            returned: success
            type: str
        username:
            description: Username of the user
            returned: success
            type: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityUserInfoModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=False, default=None),
        domain=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default=None),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    deprecated_names = ('openstack.cloud.identity_user_facts')

    def run(self):
        name = self.params['name']
        domain = self.params['domain']
        filters = self.params['filters']

        if domain:
            try:
                # We assume admin is passing domain id
                dom = self.conn.get_domain(domain)['id']
                domain = dom
            except Exception:
                # If we fail, maybe admin is passing a domain name.
                # Note that domains have unique names, just like id.
                dom = self.conn.search_domains(filters={'name': domain})
                if dom:
                    domain = dom[0]['id']
                else:
                    self.fail_json(msg='Domain name or ID does not exist')

            if not filters:
                filters = {}

            filters['domain_id'] = domain

        users = self.conn.search_users(name, filters)
        self.exit_json(changed=False, openstack_users=users)


def main():
    module = IdentityUserInfoModule()
    module()


if __name__ == '__main__':
    main()
