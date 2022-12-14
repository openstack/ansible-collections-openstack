#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2013, Benno Joy <benno@ansible.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: security_group
short_description: Manage Neutron security groups of an OpenStack cloud.
author: OpenStack Ansible SIG
description:
  - Add or remove Neutron security groups to/from an OpenStack cloud.
options:
  description:
    description:
      - Long description of the purpose of the security group.
    type: str
  name:
    description:
      - Name that has to be given to the security group. This module
        requires that security group names be unique.
    required: true
    type: str
  project:
    description:
      - Unique name or ID of the project.
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

RETURN = r'''
security_group:
  description: Dictionary describing the security group.
  type: dict
  returned: On success when I(state) is C(present).
  contains:
    created_at:
      description: Creation time of the security group
      type: str
      sample: "yyyy-mm-dd hh:mm:ss"
    description:
      description: Description of the security group
      type: str
      sample: "My security group"
    id:
      description: ID of the security group
      type: str
      sample: "d90e55ba-23bd-4d97-b722-8cb6fb485d69"
    name:
      description: Name of the security group.
      type: str
      sample: "my-sg"
    project_id:
      description: Project ID where the security group is located in.
      type: str
      sample: "25d24fc8-d019-4a34-9fff-0a09fde6a567"
    revision_number:
      description: The revision number of the resource.
      type: int
    tenant_id:
      description: Tenant ID where the security group is located in. Deprecated
      type: str
      sample: "25d24fc8-d019-4a34-9fff-0a09fde6a567"
    security_group_rules:
      description: Specifies the security group rule list
      type: list
      sample: [
        {
          "id": "d90e55ba-23bd-4d97-b722-8cb6fb485d69",
          "direction": "ingress",
          "protocol": null,
          "ethertype": "IPv4",
          "description": null,
          "remote_group_id": "0431c9c5-1660-42e0-8a00-134bec7f03e2",
          "remote_ip_prefix": null,
          "tenant_id": "bbfe8c41dd034a07bebd592bf03b4b0c",
          "port_range_max": null,
          "port_range_min": null,
          "security_group_id": "0431c9c5-1660-42e0-8a00-134bec7f03e2"
        },
        {
          "id": "aecff4d4-9ce9-489c-86a3-803aedec65f7",
          "direction": "egress",
          "protocol": null,
          "ethertype": "IPv4",
          "description": null,
          "remote_group_id": null,
          "remote_ip_prefix": null,
          "tenant_id": "bbfe8c41dd034a07bebd592bf03b4b0c",
          "port_range_max": null,
          "port_range_min": null,
          "security_group_id": "0431c9c5-1660-42e0-8a00-134bec7f03e2"
        }
      ]
    stateful:
      description: Indicates if the security group is stateful or stateless.
      type: bool
    tags:
      description: The list of tags on the resource.
      type: list
    updated_at:
      description: Update time of the security group
      type: str
      sample: "yyyy-mm-dd hh:mm:ss"
'''

EXAMPLES = r'''
- name: Create a security group
  openstack.cloud.security_group:
    cloud: mordred
    state: present
    name: foo
    description: security group for foo servers

- name: Update the existing 'foo' security group description
  openstack.cloud.security_group:
    cloud: mordred
    state: present
    name: foo
    description: updated description for the foo security group

- name: Create a security group for a given project
  openstack.cloud.security_group:
    cloud: mordred
    state: present
    name: foo
    project: myproj
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class SecurityGroupModule(OpenStackModule):

    argument_spec = dict(
        description=dict(),
        name=dict(required=True),
        project=dict(),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = dict(
        supports_check_mode=True,
    )

    def run(self):
        state = self.params['state']

        security_group = self._find()

        if self.ansible.check_mode:
            self.exit_json(changed=self._will_change(state, security_group))

        if state == 'present' and not security_group:
            # Create security_group
            security_group = self._create()
            self.exit_json(
                changed=True,
                security_group=security_group.to_dict(computed=False))

        elif state == 'present' and security_group:
            # Update security_group
            update = self._build_update(security_group)
            if update:
                security_group = self._update(security_group, update)

            self.exit_json(
                changed=bool(update),
                security_group=security_group.to_dict(computed=False))

        elif state == 'absent' and security_group:
            # Delete security_group
            self._delete(security_group)
            self.exit_json(changed=True)

        elif state == 'absent' and not security_group:
            # Do nothing
            self.exit_json(changed=False)

    def _build_update(self, security_group):
        update = {}

        # module options name and project are used to find security group
        # and thus cannot be updated

        non_updateable_keys = [k for k in []
                               if self.params[k] is not None
                               and self.params[k] != security_group[k]]

        if non_updateable_keys:
            self.fail_json(msg='Cannot update parameters {0}'
                               .format(non_updateable_keys))

        attributes = dict((k, self.params[k])
                          for k in ['description']
                          if self.params[k] is not None
                          and self.params[k] != security_group[k])

        if attributes:
            update['attributes'] = attributes

        return update

    def _create(self):
        kwargs = dict((k, self.params[k])
                      for k in ['description', 'name']
                      if self.params[k] is not None)

        project_name_or_id = self.params['project']
        if project_name_or_id is not None:
            project = self.conn.identity.find_project(
                name_or_id=project_name_or_id, ignore_missing=False)
            kwargs['project_id'] = project.id

        return self.conn.network.create_security_group(**kwargs)

    def _delete(self, security_group):
        self.conn.network.delete_security_group(security_group.id)

    def _find(self):
        kwargs = dict(name_or_id=self.params['name'])

        project_name_or_id = self.params['project']
        if project_name_or_id is not None:
            project = self.conn.identity.find_project(
                name_or_id=project_name_or_id, ignore_missing=False)
            kwargs['project_id'] = project.id

        return self.conn.network.find_security_group(**kwargs)

    def _update(self, security_group, update):
        attributes = update.get('attributes')
        if attributes:
            security_group = self.conn.network.update_security_group(
                security_group.id, **attributes)

        return security_group

    def _will_change(self, state, security_group):
        if state == 'present' and not security_group:
            return True
        elif state == 'present' and security_group:
            return bool(self._build_update(security_group))
        elif state == 'absent' and security_group:
            return True
        else:
            # state == 'absent' and not security_group:
            return False


def main():
    module = SecurityGroupModule()
    module()


if __name__ == '__main__':
    main()
