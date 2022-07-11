#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: federation_idp_info
short_description: Get the information about the available federation identity
                   providers
author: OpenStack Ansible SIG
description:
  - Fetch available federation identity providers.
options:
  name:
    description:
      - The name of the identity provider to fetch.
    type: str
    aliases: ['id']
requirements:
  - "python >= 3.6"
  - "openstacksdk"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Fetch a specific identity provider
  openstack.cloud.federation_idp_info:
    cloud: example_cloud
    name: example_provider

- name: Fetch all providers
  openstack.cloud.federation_idp_info:
    cloud: example_cloud
'''

RETURN = '''
identity_providers:
    description: Dictionary describing the identity providers
    returned: success
    type: list
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
            description: Indicates wether the identity provider is enabled
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


class IdentityFederationIdpInfoModule(OpenStackModule):
    argument_spec = dict(
        name=dict(aliases=['id']),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        """ Module entry point """

        name = self.params['name']

        query = {}
        if name:
            query["id"] = name

        idps = self.conn.identity.identity_providers(**query)
        idps = [idp.to_dict(computed=False) for idp in idps]
        self.exit_json(changed=False, identity_providers=idps)


def main():
    module = IdentityFederationIdpInfoModule()
    module()


if __name__ == '__main__':
    main()
