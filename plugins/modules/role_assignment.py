#!/usr/bin/python
# Copyright (c) 2016 IBM
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: role_assignment
short_description: Associate OpenStack Identity users and roles
author: OpenStack Ansible SIG
description:
    - Grant and revoke roles in either project or domain context for
      OpenStack Identity Users.
options:
   role:
     description:
        - Name or ID for the role.
     required: true
     type: str
   user:
     description:
        - Name or ID for the user. If I(user) is not specified, then
          I(group) is required. Both may not be specified.
     type: str
   group:
     description:
        - Name or ID for the group. Valid only with keystone version 3.
          If I(group) is not specified, then I(user) is required. Both
          may not be specified.
     type: str
   project:
     description:
        - Name or ID of the project to scope the role association to.
          If you are using keystone version 2, then this value is required.
     type: str
   domain:
     description:
        - Name or ID of the domain to scope the role association to. Valid only
          with keystone version 3, and required if I(project) is not specified.
     type: str
   state:
     description:
       - Should the roles be present or absent on the user.
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
# Grant an admin role on the user admin in the project project1
- openstack.cloud.role_assignment:
    cloud: mycloud
    user: admin
    role: admin
    project: project1

# Revoke the admin role from the user barney in the newyork domain
- openstack.cloud.role_assignment:
    cloud: mycloud
    state: absent
    user: barney
    role: admin
    domain: newyork
'''

RETURN = '''
#
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityRoleAssignmentModule(OpenStackModule):
    argument_spec = dict(
        role=dict(required=True),
        user=dict(required=False),
        group=dict(required=False),
        project=dict(required=False),
        domain=dict(required=False),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = dict(
        required_one_of=[
            ['user', 'group']
        ],
        supports_check_mode=True
    )

    def _system_state_change(self, state, assignment):
        if state == 'present' and not assignment:
            return True
        elif state == 'absent' and assignment:
            return True
        return False

    def _build_kwargs(self, user, group, project, domain):
        kwargs = {}
        if user:
            kwargs['user'] = user
        if group:
            kwargs['group'] = group
        if project:
            kwargs['project'] = project
        if domain:
            kwargs['domain'] = domain
        return kwargs

    def run(self):
        role = self.params.get('role')
        user = self.params.get('user')
        group = self.params.get('group')
        project = self.params.get('project')
        domain = self.params.get('domain')
        state = self.params.get('state')

        filters = {}
        domain_id = None

        r = self.conn.get_role(role)
        if r is None:
            self.fail_json(msg="Role %s is not valid" % role)
        filters['role'] = r['id']

        if domain:
            d = self.conn.get_domain(name_or_id=domain)
            if d is None:
                self.fail_json(msg="Domain %s is not valid" % domain)
            filters['domain'] = d['id']
            domain_id = d['id']
        if user:
            if domain:
                u = self.conn.get_user(user, domain_id=filters['domain'])
            else:
                u = self.conn.get_user(user)

            if u is None:
                self.fail_json(msg="User %s is not valid" % user)
            filters['user'] = u['id']
        if group:
            if domain:
                g = self.conn.get_group(group, domain_id=filters['domain'])
            else:
                g = self.conn.get_group(group)
            if g is None:
                self.fail_json(msg="Group %s is not valid" % group)
            filters['group'] = g['id']
        if project:
            if domain:
                p = self.conn.get_project(project, domain_id=filters['domain'])
                # OpenStack won't allow us to use both a domain and project as
                # filter. Once we identified the project (using the domain as
                # a filter criteria), we need to remove the domain itself from
                # the filters list.
                domain_id = filters.pop('domain')
            else:
                p = self.conn.get_project(project)

            if p is None:
                self.fail_json(msg="Project %s is not valid" % project)
            filters['project'] = p['id']

        assignment = self.conn.list_role_assignments(filters=filters)

        if self.ansible.check_mode:
            self.exit_json(changed=self._system_state_change(state, assignment))

        changed = False

        if state == 'present':
            if not assignment:
                kwargs = self._build_kwargs(user, group, project, domain_id)
                self.conn.grant_role(role, **kwargs)
                changed = True

        elif state == 'absent':
            if assignment:
                kwargs = self._build_kwargs(user, group, project, domain_id)
                self.conn.revoke_role(role, **kwargs)
                changed = True

        self.exit_json(changed=changed)


def main():
    module = IdentityRoleAssignmentModule()
    module()


if __name__ == '__main__':
    main()
