#!/usr/bin/python
# Copyright (c) 2016 IBM
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: identity_role
short_description: Manage OpenStack Identity Roles
author: OpenStack Ansible SIG
description:
    - Manage OpenStack Identity Roles.
options:
   name:
     description:
        - Role Name
     required: true
     type: str
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
     type: str
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Create a role named "demo"
- openstack.cloud.identity_role:
    cloud: mycloud
    state: present
    name: demo

# Delete the role named "demo"
- openstack.cloud.identity_role:
    cloud: mycloud
    state: absent
    name: demo
'''

RETURN = '''
role:
    description: Dictionary describing the role.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: Unique role ID.
            type: str
            sample: "677bfab34c844a01b88a217aa12ec4c2"
        name:
            description: Role name.
            type: str
            sample: "demo"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (openstack_full_argument_spec,
                                                                                openstack_module_kwargs,
                                                                                openstack_cloud_from_module)


def _system_state_change(state, role):
    if state == 'present' and not role:
        return True
    if state == 'absent' and role:
        return True
    return False


def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(required=True),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           **module_kwargs)

    name = module.params.get('name')
    state = module.params.get('state')

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        role = cloud.get_role(name)

        if module.check_mode:
            module.exit_json(changed=_system_state_change(state, role))

        if state == 'present':
            if role is None:
                role = cloud.create_role(name)
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed, role=role)
        elif state == 'absent':
            if role is None:
                changed = False
            else:
                cloud.delete_role(name)
                changed = True
            module.exit_json(changed=changed)

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
