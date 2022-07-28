#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 IBM Corporation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: project
short_description: Manage OpenStack Projects
author: OpenStack Ansible SIG
description:
    - Manage OpenStack Projects. Projects can be created,
      updated or deleted using this module. A project will be updated
      if I(name) matches an existing project and I(state) is present.
      The value for I(name) cannot be updated without deleting and
      re-creating the project.
options:
  name:
    description:
      - Name for the project
    required: true
    type: str
  description:
    description:
      - Description for the project
    type: str
  domain:
    description:
       - Domain name or id to create the project in if the cloud supports
         domains.
    aliases: ['domain_id']
    type: str
  is_enabled:
    description:
      - Is the project enabled
    aliases: ['enabled']
    type: bool
    default: 'yes'
  properties:
    description:
      - Additional properties to be associated with this project.
    type: dict
    required: false
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
# Create a project
- openstack.cloud.project:
    cloud: mycloud
    endpoint_type: admin
    state: present
    name: demoproject
    description: demodescription
    domain: demoid
    is_enabled: True
    properties:
      internal_alias: demo_project

# Delete a project
- openstack.cloud.project:
    cloud: mycloud
    endpoint_type: admin
    state: absent
    name: demoproject
'''


RETURN = '''
project:
    description: Dictionary describing the project.
    returned: On success when I(state) is 'present'
    type: dict
    contains:
        description:
            description: Project description
            type: str
            sample: "demodescription"
        domain_id:
            description: domain to which the project belongs
            type: str
            sample: "default"
        id:
            description: Project ID
            type: str
            sample: "f59382db809c43139982ca4189404650"
        is_domain:
            description: Indicates whether the project also acts as a domain.
            type: bool
        is_enabled:
            description: Indicates whether the project is enabled
            type: bool
        name:
            description: Project name
            type: str
            sample: "demoproject"
        options:
            description: The resource options for the project
            type: dict
        parent_id:
            description: The ID of the parent of the project
            type: str
        tags:
            description: A list of associated tags
            type: list
            elements: str
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityProjectModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=True),
        description=dict(),
        domain=dict(aliases=['domain_id']),
        is_enabled=dict(default=True, type='bool', aliases=['enabled']),
        properties=dict(type='dict', min_ver='0.45.1'),
        state=dict(default='present', choices=['absent', 'present'])
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def _needs_update(self, project, update, extra):
        # We cannot update a project name because name find projects by name so
        # only a project with an already matching name will be considered for
        # updates
        keys = ('description', 'is_enabled')
        if any((k in update and update[k] != project[k]) for k in keys):
            return True

        # Additional keys passed by user will be checked completely
        if extra and any(k not in project or extra[k] != project[k]
                         for k in extra.keys()):
            return True

        return False

    def _get_domain_id(self, domain):
        dom_obj = self.conn.identity.find_domain(domain)
        if dom_obj is None:
            # Ok, let's hope the user is non-admin and passing a sane id
            return domain
        return dom_obj.id

    def _system_state_change(self, state, project, attrs, extra_attrs):
        if state == 'present':
            if project is None:
                return True
            return self._needs_update(project, attrs, extra_attrs)
        # Else state is absent
        return project is not None

    def run(self):
        name = self.params['name']
        domain = self.params['domain']
        state = self.params['state']
        properties = self.params['properties']
        enabled = self.params['is_enabled']
        description = self.params['description']

        find_project_kwargs = {}
        domain_id = None
        if domain:
            domain_id = self._get_domain_id(domain)
            find_project_kwargs['domain_id'] = domain_id

        project = None
        if name is not None:
            project = self.conn.identity.find_project(
                name, **find_project_kwargs)

        project_attrs = {
            'name': name,
            'description': description,
            'is_enabled': enabled,
            'domain_id': domain_id,
        }
        project_attrs = {k: v for k, v in project_attrs.items()
                         if v is not None}
        # Add in arbitrary properties
        if properties:
            project_attrs.update(properties)

        if self.check_mode:
            self.exit_json(changed=self._system_state_change(state, project,
                                                             project_attrs,
                                                             properties))

        changed = False
        if state == 'present':
            if project is None:
                project = self.conn.identity.create_project(**project_attrs)
                changed = True
            elif self._needs_update(project, project_attrs, properties):
                project = self.conn.identity.update_project(
                    project, **project_attrs)
                changed = True
            self.exit_json(changed=changed,
                           project=project.to_dict(computed=False))
        elif state == 'absent' and project is not None:
            self.conn.identity.delete_project(project['id'])
            changed = True
        self.exit_json(changed=changed)


def main():
    module = IdentityProjectModule()
    module()


if __name__ == '__main__':
    main()
