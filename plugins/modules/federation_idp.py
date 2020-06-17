#!/usr/bin/python
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
        return None

    _idp = idp.to_dict()
    _idp['enabled'] = idp['is_enabled']
    _idp['name'] = idp['id']
    return _idp


def delete_identity_provider(module, sdk, cloud, idp):
    """
    Delete an existing Identity Provider

    returns: the "Changed" state
    """

    if idp is None:
        return False

    if module.check_mode:
        return True

    try:
        cloud.identity.delete_identity_provider(idp)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to delete identity provider: {0}'.format(str(ex)))
    return True


def create_identity_provider(module, sdk, cloud, name):
    """
    Create a new Identity Provider

    returns: the "Changed" state and the new identity provider
    """

    if module.check_mode:
        return True, None

    description = module.params.get('description')
    enabled = module.params.get('enabled')
    domain_id = module.params.get('domain_id')
    remote_ids = module.params.get('remote_ids')

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

    try:
        idp = cloud.identity.create_identity_provider(id=name, **attributes)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to create identity provider: {0}'.format(str(ex)))
    return (True, idp)


def update_identity_provider(module, sdk, cloud, idp):
    """
    Update an existing Identity Provider

    returns: the "Changed" state and the new identity provider
    """

    description = module.params.get('description')
    enabled = module.params.get('enabled')
    domain_id = module.params.get('domain_id')
    remote_ids = module.params.get('remote_ids')

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
        return False, idp

    if module.check_mode:
        return True, None

    try:
        new_idp = cloud.identity.update_identity_provider(idp, **attributes)
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to update identity provider: {0}'.format(str(ex)))
    return (True, new_idp)


def main():
    """ Module entry point """

    argument_spec = openstack_full_argument_spec(
        name=dict(required=True, aliases=['id']),
        state=dict(default='present', choices=['absent', 'present']),
        description=dict(),
        domain_id=dict(),
        enabled=dict(type='bool', aliases=['is_enabled']),
        remote_ids=dict(type='list', elements='str'),
    )
    module_kwargs = openstack_module_kwargs(
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    name = module.params.get('name')
    state = module.params.get('state')
    changed = False

    sdk, cloud = openstack_cloud_from_module(module, min_version="0.44")

    try:
        idp = cloud.identity.get_identity_provider(name)
    except sdk.exceptions.ResourceNotFound:
        idp = None
    except sdk.exceptions.OpenStackCloudException as ex:
        module.fail_json(msg='Failed to get identity provider: {0}'.format(str(ex)))

    if state == 'absent':
        if idp is not None:
            changed = delete_identity_provider(module, sdk, cloud, idp)
        module.exit_json(changed=changed)

    # state == 'present'
    else:
        if idp is None:
            if module.params.get('domain_id') is None:
                module.fail_json(msg='A domain_id must be passed when creating'
                                 ' an identity provider')
            (changed, idp) = create_identity_provider(module, sdk, cloud, name)
            idp = normalize_idp(idp)
            module.exit_json(changed=changed, identity_provider=idp)

        (changed, new_idp) = update_identity_provider(module, sdk, cloud, idp)
        new_idp = normalize_idp(new_idp)
        module.exit_json(changed=changed, identity_provider=new_idp)


if __name__ == '__main__':
    main()
