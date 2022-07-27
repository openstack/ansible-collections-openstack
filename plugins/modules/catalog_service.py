#!/usr/bin/python
# Copyright 2016 Sam Yaple
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: catalog_service
short_description: Manage OpenStack Identity services
author: OpenStack Ansible SIG
description:
    - Create, update, or delete OpenStack Identity service. If a service
      with the supplied name already exists, it will be updated with the
      new description and enabled attributes.
options:
   name:
     description:
        - Name of the service
     required: true
     type: str
   description:
     description:
        - Description of the service
     type: str
   is_enabled:
     description:
        - Is the service enabled
     type: bool
     default: 'yes'
     aliases: ['enabled']
   type:
     description:
        - The type of service
     required: true
     type: str
     aliases: ['service_type']
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
# Create a service for glance
- openstack.cloud.catalog_service:
     cloud: mycloud
     state: present
     name: glance
     type: image
     description: OpenStack Image Service
# Delete a service
- openstack.cloud.catalog_service:
     cloud: mycloud
     state: absent
     name: glance
     type: image
'''

RETURN = '''
service:
    description: Dictionary describing the service.
    returned: On success when I(state) is 'present'
    type: dict
    contains:
        id:
            description: Service ID.
            type: str
            sample: "3292f020780b4d5baf27ff7e1d224c44"
        name:
            description: Service name.
            type: str
            sample: "glance"
        type:
            description: Service type.
            type: str
            sample: "image"
        description:
            description: Service description.
            type: str
            sample: "OpenStack Image Service"
        is_enabled:
            description: Service status.
            type: bool
            sample: True
        links:
            description: Link of the service
            type: str
            sample: http://10.0.0.1/identity/v3/services/0ae87
id:
    description: The service ID.
    returned: On success when I(state) is 'present'
    type: str
    sample: "3292f020780b4d5baf27ff7e1d224c44"
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityCatalogServiceModule(OpenStackModule):
    argument_spec = dict(
        description=dict(),
        is_enabled=dict(default=True, aliases=['enabled'], type='bool'),
        name=dict(required=True),
        type=dict(required=True, aliases=['service_type']),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = dict(
        supports_check_mode=True
    )

    def _needs_update(self, service):
        for parameter in ('is_enabled', 'description', 'type'):
            if service[parameter] != self.params[parameter]:
                return True
        return False

    def _system_state_change(self, service):
        state = self.params['state']
        if state == 'absent' and service:
            return True

        if state == 'present':
            if service is None:
                return True
            return self._needs_update(service)

        return False

    def run(self):
        description = self.params['description']
        enabled = self.params['is_enabled']
        name = self.params['name']
        state = self.params['state']
        type = self.params['type']

        filters = {'name': name, 'type': type}

        services = list(self.conn.identity.services(**filters))

        service = None
        if len(services) > 1:
            self.fail_json(
                msg='Service name %s and type %s are not unique'
                % (name, type))
        elif len(services) == 1:
            service = services[0]

        if self.ansible.check_mode:
            self.exit_json(changed=self._system_state_change(service))

        args = {'name': name, 'enabled': enabled, 'type': type}
        if description:
            args['description'] = description

        if state == 'present':
            if service is None:
                service = self.conn.identity.create_service(**args)
                changed = True
            else:
                if self._needs_update(service):
                    # The self.conn.update_service calls get_service that
                    # checks if the service is duplicated or not. We don't need
                    # to do it here because it was already checked above
                    service = self.conn.identity.update_service(service,
                                                                **args)
                    changed = True
                else:
                    changed = False
            service = service.to_dict(computed=False)
            self.exit_json(changed=changed, service=service, id=service['id'])

        elif state == 'absent':
            if service is None:
                changed = False
            else:
                self.conn.identity.delete_service(service)
                changed = True
            self.exit_json(changed=changed)


def main():
    module = IdentityCatalogServiceModule()
    module()


if __name__ == '__main__':
    main()
