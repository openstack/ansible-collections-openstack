#!/usr/bin/python

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: image_info
short_description: Retrieve information about an image within OpenStack.
author: OpenStack Ansible SIG
description:
    - Retrieve information about a image image from OpenStack.
    - This module was called C(openstack.cloud.image_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(openstack.cloud.image_info) module no longer returns C(ansible_facts)!
options:
   image:
     description:
        - Name or ID of the image
     required: false
     type: str
   properties:
     description:
        - Dict of properties of the images used for query
     type: dict
     required: false
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
- name: Gather information about a previously created image named image1
  openstack.cloud.image_info:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    image: image1
  register: result

- name: Show openstack information
  debug:
    msg: "{{ result.openstack_image }}"

# Show all available Openstack images
- name: Retrieve all available Openstack images
  openstack.cloud.image_info:
  register: result

- name: Show images
  debug:
    msg: "{{ result.openstack_image }}"

# Show images matching requested properties
- name: Retrieve images having properties with desired values
  openstack.cloud.image_facts:
    properties:
      some_property: some_value
      OtherProp: OtherVal

- name: Show images
  debug:
    msg: "{{ result.openstack_image }}"
'''

RETURN = '''
openstack_image:
    description: has all the openstack information about the image
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: str
        name:
            description: Name given to the image.
            returned: success
            type: str
        status:
            description: Image status.
            returned: success
            type: str
        created_at:
            description: Image created at timestamp.
            returned: success
            type: str
        deleted:
            description: Image deleted flag.
            returned: success
            type: bool
        container_format:
            description: Container format of the image.
            returned: success
            type: str
        min_ram:
            description: Min amount of RAM required for this image.
            returned: success
            type: int
        disk_format:
            description: Disk format of the image.
            returned: success
            type: str
        updated_at:
            description: Image updated at timestamp.
            returned: success
            type: str
        properties:
            description: Additional properties associated with the image.
            returned: success
            type: dict
        min_disk:
            description: Min amount of disk space required for this image.
            returned: success
            type: int
        protected:
            description: Image protected flag.
            returned: success
            type: bool
        checksum:
            description: Checksum for the image.
            returned: success
            type: str
        owner:
            description: Owner for the image.
            returned: success
            type: str
        is_public:
            description: Is public flag of the image.
            returned: success
            type: bool
        deleted_at:
            description: Image deleted at timestamp.
            returned: success
            type: str
        size:
            description: Size of the image.
            returned: success
            type: int
        tags:
            description: List of tags assigned to the image
            returned: success
            type: list
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class ImageInfoModule(OpenStackModule):

    deprecated_names = ('openstack.cloud.os_image_facts', 'openstack.cloud.os_image_info')

    argument_spec = dict(
        image=dict(type='str', required=False),
        properties=dict(type='dict', required=False),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):

        if self.params['image']:
            image = self.conn.get_image(self.params['image'])
            self.exit(changed=False, openstack_image=image)
        else:
            images = self.conn.search_images(filters=self.params['properties'])
            self.exit(changed=False, openstack_image=images)


def main():
    module = ImageInfoModule()
    module()


if __name__ == '__main__':
    main()
