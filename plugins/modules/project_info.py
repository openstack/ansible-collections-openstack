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
    - This module was called C(openstack.cloud.project_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(openstack.cloud.project_info) module no longer returns C(ansible_facts)!
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
      enabled: False
  register: result
- debug:
    msg: "{{ result.openstack_projects }}"
'''


RETURN = '''
openstack_projects:
    description: has all the OpenStack information about projects
    returned: always, but can be null
    type: complex
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
        enabled:
            description: Flag to indicate if the project is enabled
            returned: success
            type: bool
        domain_id:
            description: Domain ID containing the project (keystone v3 clouds only)
            returned: success
            type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        name=dict(required=False, default=None),
        domain=dict(required=False, default=None),
        filters=dict(required=False, type='dict', default=None),
    )

    module = AnsibleModule(argument_spec)
    is_old_facts = module._name == 'openstack.cloud.project_facts'
    if is_old_facts:
        module.deprecate("The 'openstack.cloud.project_facts' module has been renamed to 'openstack.cloud.project_info', "
                         "and the renamed one no longer returns ansible_facts", version='2.13')

    sdk, opcloud = openstack_cloud_from_module(module)
    try:
        name = module.params['name']
        domain = module.params['domain']
        filters = module.params['filters']

        if domain:
            try:
                # We assume admin is passing domain id
                dom = opcloud.get_domain(domain)['id']
                domain = dom
            except Exception:
                # If we fail, maybe admin is passing a domain name.
                # Note that domains have unique names, just like id.
                dom = opcloud.search_domains(filters={'name': domain})
                if dom:
                    domain = dom[0]['id']
                else:
                    module.fail_json(msg='Domain name or ID does not exist')

            if not filters:
                filters = {}

            filters['domain_id'] = domain

        projects = opcloud.search_projects(name, filters)
        if is_old_facts:
            module.exit_json(changed=False, ansible_facts=dict(
                openstack_projects=projects))
        else:
            module.exit_json(changed=False, openstack_projects=projects)

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
