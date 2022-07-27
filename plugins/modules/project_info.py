#!/usr/bin/python
# Copyright (c) 2016 Hewlett-Packard Enterprise Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: project_info
short_description: Retrieve information about one or more OpenStack projects
author: OpenStack Ansible SIG
description:
    - Retrieve information about a one or more OpenStack projects
options:
   name:
     description:
        - Name or ID of the project
     type: str
   domain:
     description:
        - Name or ID of the domain containing the project if the cloud supports domains
     type: str
   filters:
     description:
        - A dictionary of meta data to use for filtering projects. Elements of
          this dictionary are parsed as queries for openstack identity api in
          the new openstacksdk.
     type: dict
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Gather information about previously created projects
- openstack.cloud.project_info:
    cloud: awesomecloud
  register: result
- debug:
    msg: "{{ result.openstack_projects }}"

# Gather information about a previously created project by name
- openstack.cloud.project_info:
    cloud: awesomecloud
    name: demoproject
  register: result
- debug:
    msg: "{{ result.openstack_projects }}"

# Gather information about a previously created project in a specific domain
- openstack.cloud.project_info:
    cloud: awesomecloud
    name: demoproject
    domain: admindomain
  register: result
- debug:
    msg: "{{ result.openstack_projects }}"

# Gather information about a previously created project in a specific domain with filter
- openstack.cloud.project_info:
    cloud: awesomecloud
    name: demoproject
    domain: admindomain
    filters:
      is_enabled: False
  register: result
- debug:
    msg: "{{ result.openstack_projects }}"
'''


RETURN = '''
openstack_projects:
    description: has all the OpenStack information about projects
    elements: dict
    returned: always, but can be empty
    type: list
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: str
        name:
            description: Name given to the project.
            returned: success
            type: str
        description:
            description: Description of the project
            returned: success
            type: str
        is_enabled:
            description: Flag to indicate if the project is enabled
            returned: success
            type: bool
        domain_id:
            description: Domain ID containing the project (keystone v3 clouds only)
            returned: success
            type: bool
        tags:
            description: A list of simple strings assigned to a project
            returned: success
            type: list
        parent_id:
            description: The ID of the parent for the project
            returned: success
            type: str
        is_domain:
            description: Indicates whether the project also acts as a domain.
            returned: success
            type: bool
        options:
            description: Set of options for the project
            returned: success
            type: dict
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityProjectInfoModule(OpenStackModule):
    argument_spec = dict(
        name=dict(),
        domain=dict(),
        filters=dict(type='dict'),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        name = self.params['name']
        domain = self.params['domain']
        filters = self.params['filters'] or {}

        if domain:
            filters['domain_id'] = self.conn.identity.find_domain(
                domain, ignore_missing=False).id

        projects = self.conn.search_projects(name, filters=filters)
        projects = [p.to_dict(computed=False) for p in projects]

        self.exit_json(changed=False, openstack_projects=projects)


def main():
    module = IdentityProjectInfoModule()
    module()


if __name__ == '__main__':
    main()
