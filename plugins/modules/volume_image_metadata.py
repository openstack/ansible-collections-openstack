#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 by Pure Storage, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: volume_image_metadata
short_description: Manage OpenStack Cinder volume image metadata
extends_documentation_fragment:
  - openstack.cloud.openstack
description:
  - Set image metadata on a Cinder volume.
  - This maps to the Cinder C(os-set_image_metadata) API action.
  - This is distinct from regular volume metadata.
options:
  volume:
    description:
      - Volume ID or name.
    required: true
    type: str
  image_metadata:
    description:
      - Image metadata to apply to the volume.
    required: true
    type: dict
author:
  - Simon Dodsley (@simondodsley)
"""

EXAMPLES = r"""
- name: Apply volume image metadata
  openstack.cloud.volume_image_metadata:
    cloud: mycloud
    volume: 9c6b7c8d-1234
    image_metadata:
      image_id: 2e1a...
      disk_format: qcow2
      container_format: bare
"""

RETURN = r"""
changed:
  description: Whether the volume image metadata was changed.
  returned: always
  type: bool
volume:
  description: Volume information.
  returned: always
  type: dict
"""

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule,
)


class VolumeImageMetadataModule(OpenStackModule):

    argument_spec = dict(
        volume=dict(required=True),
        image_metadata=dict(type="dict", required=True),
    )

    module_kwargs = dict(
        supports_check_mode=True,
    )

    def run(self):
        volume_ref = self.params["volume"]
        desired_meta = self.params["image_metadata"]

        # Resolve volume
        volume = self.conn.block_storage.find_volume(volume_ref, ignore_missing=False)

        current_meta = volume.volume_image_metadata or {}

        # Idempotency check
        if desired_meta.items() <= current_meta.items():
            self.exit_json(changed=False, volume=volume.to_dict())

        if not self.ansible.check_mode:
            self.conn.block_storage.set_volume_image_metadata(volume.id, **desired_meta)

        volume = self.conn.block_storage.get_volume(volume.id)

        self.exit_json(changed=True, volume=volume.to_dict())


def main():
    module = VolumeImageMetadataModule()
    module()


if __name__ == "__main__":
    main()
