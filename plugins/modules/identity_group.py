#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 IBM
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: identity_group
short_description: Manage OpenStack Identity Groups
author: OpenStack Ansible SIG
description:
    - Manage OpenStack Identity Groups. Groups can be created, deleted or
      updated. Only the I(description) value can be updated.
options:
   description:
     description:
        - Group description
     type: str
   domain_id:
     description:
        - Domain id to create the group in if the cloud supports domains.
     type: str
   name:
     description:
        - Group name
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
# Create a group named "demo"
- openstack.cloud.identity_group:
    cloud: mycloud
    state: present
    name: demo
    description: "Demo Group"
    domain_id: demoid

# Update the description on existing "demo" group
- openstack.cloud.identity_group:
    cloud: mycloud
    state: present
    name: demo
    description: "Something else"
    domain_id: demoid

# Delete group named "demo"
- openstack.cloud.identity_group:
    cloud: mycloud
    state: absent
    name: demo
'''

RETURN = '''
group:
    description: Dictionary describing the group.
    returned: On success when I(state) is 'present'.
    type: dict
    contains:
        description:
            description: Group description
            type: str
            sample: "Demo Group"
        domain_id:
            description: Domain for the group
            type: str
            sample: "default"
        id:
            description: Unique group ID
            type: str
            sample: "ee6156ff04c645f481a6738311aea0b0"
        name:
            description: Group name
            type: str
            sample: "demo"
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityGroupModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        domain_id=dict(),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def _system_state_change(self, state, group):
        if state == 'present' and not group:
            return True
        if state == 'present' and self._build_update(group):
            return True
        if state == 'absent' and group:
            return True
        return False

    def _build_update(self, group):
        update = {}
        desc = self.params['description']
        if desc is not None and desc != group.description:
            update['description'] = desc
        return update

    def run(self):
        name = self.params['name']
        description = self.params['description']
        state = self.params['state']
        domain_id = self.params['domain_id']

        group_filters = {}
        if domain_id is not None:
            group_filters['domain_id'] = domain_id

        group = self.conn.identity.find_group(name, **group_filters)

        if self.ansible.check_mode:
            self.exit_json(changed=self._system_state_change(state, group))

        changed = False
        if state == 'present':
            if group is None:
                kwargs = dict(description=description, domain_id=domain_id)
                kwargs = {k: v for k, v in kwargs.items() if v is not None}
                group = self.conn.identity.create_group(
                    name=name, **kwargs)
                changed = True
            else:
                update = self._build_update(group)
                if update:
                    group = self.conn.identity.update_group(group, **update)
                    changed = True
            group = group.to_dict(computed=False)
            self.exit_json(changed=changed, group=group)

        elif state == 'absent' and group is not None:
            self.conn.identity.delete_group(group)
            changed = True
        self.exit_json(changed=changed)


def main():
    module = IdentityGroupModule()
    module()


if __name__ == '__main__':
    main()
