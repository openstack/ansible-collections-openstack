#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: federation_idp
short_description: manage a federation Identity Provider
author: OpenStack Ansible SIG
description:
  - Manage a federation Identity Provider.
options:
  name:
    description:
      - The name of the Identity Provider.
    type: str
    required: true
    aliases: ['id']
  state:
    description:
      - Whether the Identity Provider should be C(present) or C(absent).
    choices: ['present', 'absent']
    default: present
    type: str
  description:
    description:
      - The description of the Identity Provider.
    type: str
  domain_id:
    description:
      - The ID of a domain that is associated with the Identity Provider.
        Federated users that authenticate with the Identity Provider will be
        created under the domain specified.
      - Required when creating a new Identity Provider.
    type: str
  enabled:
    description:
      - Whether the Identity Provider is enabled or not.
      - Will default to C(true) when creating a new Identity Provider.
    type: bool
    aliases: ['is_enabled']
  remote_ids:
    description:
      - "List of the unique Identity Provider's remote IDs."
      - Will default to an empty list when creating a new Identity Provider.
    type: list
    elements: str
requirements:
  - "python >= 3.6"
  - "openstacksdk >= 0.44"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Create an identity provider
  openstack.cloud.federation_idp:
    cloud: example_cloud
    name: example_provider
    domain_id: 0123456789abcdef0123456789abcdef
    description: 'My example IDP'
    remote_ids:
    - 'https://auth.example.com/auth/realms/ExampleRealm'

- name: Delete an identity provider
  openstack.cloud.federation_idp:
    cloud: example_cloud
    name: example_provider
    state: absent
'''

RETURN = '''
identity_provider:
    description: Dictionary describing the identity providers
    returned: On success when I(state) is 'present'
    type: dict
    elements: dict
    contains:
        description:
            description: Identity provider description
            type: str
            sample: "demodescription"
        domain_id:
            description: Domain to which the identity provider belongs
            type: str
            sample: "default"
        id:
            description: Identity provider ID
            type: str
            sample: "test-idp"
        is_enabled:
            description: Indicates whether the identity provider is enabled
            type: bool
        name:
            description: Name of the identity provider, equals its ID.
            type: str
            sample: "test-idp"
        remote_ids:
            description: Remote IDs associated with the identity provider
            type: list
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class IdentityFederationIdpModule(OpenStackModule):
    argument_spec = dict(
        name=dict(required=True, aliases=['id']),
        state=dict(default='present', choices=['absent', 'present']),
        description=dict(),
        domain_id=dict(),
        enabled=dict(type='bool', aliases=['is_enabled']),
        remote_ids=dict(type='list', elements='str'),
    )
    module_kwargs = dict(
        supports_check_mode=True,
    )

    def delete_identity_provider(self, idp):
        """
        Delete an existing Identity Provider

        returns: the "Changed" state
        """
        if idp is None:
            return False

        if self.ansible.check_mode:
            return True

        self.conn.identity.delete_identity_provider(idp)
        return True

    def create_identity_provider(self, name):
        """
        Create a new Identity Provider

        returns: the "Changed" state and the new identity provider
        """

        if self.ansible.check_mode:
            return True, None

        description = self.params.get('description')
        enabled = self.params.get('enabled')
        domain_id = self.params.get('domain_id')
        remote_ids = self.params.get('remote_ids')

        if enabled is None:
            enabled = True
        if remote_ids is None:
            remote_ids = []

        attributes = {
            'domain_id': domain_id,
            'enabled': enabled,
            'remote_ids': remote_ids,
        }
        if description is not None:
            attributes['description'] = description

        idp = self.conn.identity.create_identity_provider(id=name, **attributes)
        return (True, idp.to_dict(computed=False))

    def update_identity_provider(self, idp):
        """
        Update an existing Identity Provider

        returns: the "Changed" state and the new identity provider
        """

        description = self.params.get('description')
        enabled = self.params.get('enabled')
        domain_id = self.params.get('domain_id')
        remote_ids = self.params.get('remote_ids')

        attributes = {}

        if (description is not None) and (description != idp.description):
            attributes['description'] = description
        if (enabled is not None) and (enabled != idp.is_enabled):
            attributes['enabled'] = enabled
        if (domain_id is not None) and (domain_id != idp.domain_id):
            attributes['domain_id'] = domain_id
        if (remote_ids is not None) and (remote_ids != idp.remote_ids):
            attributes['remote_ids'] = remote_ids

        if not attributes:
            return False, idp.to_dict(computed=False)

        if self.ansible.check_mode:
            return True, None

        new_idp = self.conn.identity.update_identity_provider(idp, **attributes)
        return (True, new_idp.to_dict(computed=False))

    def run(self):
        """ Module entry point """

        name = self.params.get('name')
        state = self.params.get('state')
        changed = False

        idp = self.conn.identity.find_identity_provider(name)

        if state == 'absent':
            if idp is not None:
                changed = self.delete_identity_provider(idp)
            self.exit_json(changed=changed)

        # state == 'present'
        else:
            if idp is None:
                if self.params.get('domain_id') is None:
                    self.fail_json(msg='A domain_id must be passed when creating'
                                   ' an identity provider')
                (changed, idp) = self.create_identity_provider(name)
                self.exit_json(changed=changed, identity_provider=idp)

            (changed, new_idp) = self.update_identity_provider(idp)
            self.exit_json(changed=changed, identity_provider=new_idp)


def main():
    module = IdentityFederationIdpModule()
    module()


if __name__ == '__main__':
    main()
