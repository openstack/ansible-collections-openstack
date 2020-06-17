#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: federation_idp_info
short_description: Get the information about the available federation identity
                   providers
author: OpenStack Ansible SIG
description:
  - Fetch a federation identity provider.
options:
  name:
    description:
      - The name of the identity provider to fetch.
      - If I(name) is specified, the module will return failed if the identity
        provider doesn't exist.
    type: str
    aliases: ['id']
requirements:
  - "python >= 3.6"
  - "openstacksdk >= 0.44"
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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_full_argument_spec
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_module_kwargs
from ansible_collections.openstack.cloud.plugins.module_utils.openstack import openstack_cloud_from_module


def normalize_idp(idp):
    """
    Normalizes the IDP definitions so that the outputs are consistent with the
    parameters

    - "enabled" (parameter) == "is_enabled" (SDK)
    - "name" (parameter) == "id" (SDK)
    """
    if idp is None:
        return

    _idp = idp.to_dict()
    _idp['enabled'] = idp['is_enabled']
    _idp['name'] = idp['id']
    return _idp


def main():
    """ Module entry point """

    argument_spec = openstack_full_argument_spec(
        name=dict(aliases=['id']),
    )
    module_kwargs = openstack_module_kwargs(
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params.get('name')

    sdk, cloud = openstack_cloud_from_module(module, min_version="0.44")

    if name:
        try:
            idp = normalize_idp(cloud.identity.get_identity_provider(name))
        except sdk.exceptions.ResourceNotFound:
            module.fail_json(msg='Failed to find identity provider')
        except sdk.exceptions.OpenStackCloudException as ex:
            module.fail_json(msg='Failed to get identity provider: {0}'.format(str(ex)))
        module.exit_json(changed=False, identity_providers=[idp])

    else:
        try:
            providers = list(map(normalize_idp, cloud.identity.identity_providers()))
        except sdk.exceptions.OpenStackCloudException as ex:
            module.fail_json(msg='Failed to list identity providers: {0}'.format(str(ex)))
        module.exit_json(changed=False, identity_providers=providers)


if __name__ == '__main__':
    main()
