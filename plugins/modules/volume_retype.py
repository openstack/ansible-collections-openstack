#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024 OpenStack Ansible Contributors
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: volume_retype
short_description: Retype (change the volume type of) a Cinder block storage volume
author: Simon Dodsley (@simondodsley)
description:
  - Change the volume type of an existing OpenStack Block Storage (Cinder) volume.
  - This operation may trigger a data migration between storage backends, depending
    on the chosen C(migration_policy).
  - The volume must be in C(available) or C(in-use) status to be retyped.
  - Retyping an in-use volume from a multiattach-capable type to a
    non-multiattach-capable type (or vice-versa) is not supported by Cinder.
  - Retyping an encrypted volume to an unencrypted volume (or vice-versa) is not
    supported by Cinder.
options:
  volume:
    description:
      - Name or ID of the volume to retype.
    type: str
    required: true
    aliases: ['name']
  new_type:
    description:
      - Name or ID of the target volume type.
    type: str
    required: true
  migration_policy:
    description:
      - Migration policy to apply when changing the volume type.
      - C(never) changes the volume type metadata only, without migrating data.
        This only works when the source and target types share the same storage
        backend. This is the Cinder default.
      - C(on-demand) triggers a full data migration to the backend associated
        with the new volume type. This allows moving between different backends
        but may take a significant amount of time depending on volume size.
    type: str
    choices: ['never', 'on-demand']
    default: 'never'
  wait:
    description:
      - Whether to wait for the retype operation to complete before returning.
      - When I(wait=true) and I(migration_policy=on-demand) the module will
        poll until the volume C(migration_status) is C(success) or C(error).
      - When I(wait=true) and I(migration_policy=never) the module waits until
        the volume returns to C(available) status.
    type: bool
    default: true
  timeout:
    description:
      - How long (in seconds) to wait for the retype operation to complete.
      - Ignored when I(wait=false).
    type: int
    default: 600
version_added: 2.6.0
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

EXAMPLES = r'''
- name: Retype a volume using the default "never" migration policy
  openstack.cloud.volume_retype:
    cloud: mycloud
    volume: my-volume
    new_type: ssd-standard

- name: Retype a volume with on-demand migration (moves data to the new backend)
  openstack.cloud.volume_retype:
    cloud: mycloud
    volume: my-volume
    new_type: high-iops
    migration_policy: on-demand
    timeout: 1800

- name: Retype a volume without waiting for completion
  openstack.cloud.volume_retype:
    cloud: mycloud
    volume: my-volume
    new_type: cold-storage
    migration_policy: on-demand
    wait: false

- name: Retype volume identified by UUID
  openstack.cloud.volume_retype:
    cloud: mycloud
    volume: a1b2c3d4-1234-5678-abcd-ef0123456789
    new_type: replicated-ssd
    migration_policy: on-demand
'''

RETURN = r'''
volume:
  description: Dictionary describing the volume after the retype operation.
  returned: On success.
  type: dict
  contains:
    attachments:
      description: Instance attachments for the volume.
      type: list
      elements: dict
    availability_zone:
      description: The availability zone of the volume.
      type: str
    bootable:
      description: Whether the volume is bootable.
      type: bool
    consistencygroup_id:
      description: The ID of the consistency group that the volume belongs to.
      type: str
    created_at:
      description: Timestamp of when the volume was created.
      type: str
    description:
      description: Human-readable description of the volume.
      type: str
    encrypted:
      description: Whether the volume is encrypted.
      type: bool
    id:
      description: Unique ID of the volume.
      type: str
    metadata:
      description: Metadata associated with the volume.
      type: dict
    migration_status:
      description:
        - Status of the most recent migration operation.
        - Will be C(success) after a successful on-demand retype.
      type: str
    name:
      description: Name of the volume.
      type: str
    replication_status:
      description: Replication status of the volume.
      type: str
    size:
      description: Volume size in GiB.
      type: int
    snapshot_id:
      description: Snapshot ID from which the volume was created.
      type: str
    source_volid:
      description: ID of the source volume, if the volume was cloned from another.
      type: str
    status:
      description: Volume status. Will be C(available) after a successful retype.
      type: str
    updated_at:
      description: Timestamp of the most recent volume update.
      type: str
    volume_type:
      description: The volume type of the volume after the retype.
      type: str
    volume_type_id:
      description: The ID of the volume type after the retype.
      type: str
'''

import time

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import (
    OpenStackModule,
)


class VolumeRetypeModule(OpenStackModule):

    argument_spec = dict(
        volume=dict(required=True, aliases=['name']),
        new_type=dict(required=True),
        migration_policy=dict(
            default='never',
            choices=['never', 'on-demand'],
        ),
        wait=dict(type='bool', default=True),
        timeout=dict(type='int', default=600),
    )

    module_kwargs = dict(
        supports_check_mode=True,
    )

    def _get_volume(self, name_or_id):
        """Retrieve the Cinder volume resource, failing if not found."""
        volume = self.conn.block_storage.find_volume(
            name_or_id, ignore_missing=False
        )
        return volume

    def _get_volume_type(self, name_or_id):
        """Retrieve the Cinder volume type resource, failing if not found.

        Uses the v3 proxy's find_type(name_or_id, ignore_missing=False) which
        accepts both names and UUIDs and raises NotFoundException on miss.
        """
        return self.conn.block_storage.find_type(
            name_or_id, ignore_missing=False
        )

    def _volume_needs_retype(self, volume, target_type):
        """Return True when the volume's current type differs from the target."""
        # openstacksdk Volume resources expose volume_type (name) and
        # volume_type_id; compare by ID when available, fall back to name.
        if volume.volume_type_id and target_type.id:
            return volume.volume_type_id != target_type.id
        return (volume.volume_type or '').lower() != (target_type.name or '').lower()

    def _wait_for_retype(self, volume_id, migration_policy, timeout):
        """
        Block until the volume completes the retype, or raise on timeout/error.

        For on-demand policy:  poll migration_status until 'success' or 'error'.
        For never policy:      poll status until 'available' or an error state.
        """
        error_statuses = {'error', 'error_deleting', 'error_restoring',
                          'error_extending', 'error_managing'}

        deadline = time.time() + timeout
        while time.time() < deadline:
            volume = self.conn.block_storage.get_volume(volume_id)

            if migration_policy == 'on-demand':
                migration_status = getattr(volume, 'migration_status', None) or ''
                if migration_status == 'success':
                    return volume
                if migration_status == 'error':
                    self.fail_json(
                        msg="Volume retype migration failed: migration_status=error",
                        volume=volume.to_dict(),
                    )
            else:  # migration_policy == 'never'
                status = (volume.status or '').lower()
                if status == 'available':
                    return volume
                if status in error_statuses:
                    self.fail_json(
                        msg="Volume entered error state during retype: "
                            "status={0}".format(volume.status),
                        volume=volume.to_dict(),
                    )

            time.sleep(5)

        self.fail_json(
            msg="Timed out waiting for volume retype to complete after "
                "{0} seconds.".format(timeout)
        )

    def run(self):
        volume_param = self.params['volume']
        new_type_param = self.params['new_type']
        migration_policy = self.params['migration_policy']
        wait = self.params['wait']
        timeout = self.params['timeout']

        # ---- Resolve the volume ----
        volume = self._get_volume(volume_param)

        # ---- Resolve the target volume type ----
        target_type = self._get_volume_type(new_type_param)

        # ---- Idempotency check ----
        if not self._volume_needs_retype(volume, target_type):
            self.exit_json(
                changed=False,
                volume=volume.to_dict(),
            )

        # ---- Validate volume status ----
        allowed_statuses = {'available', 'in-use'}
        if (volume.status or '').lower() not in allowed_statuses:
            self.fail_json(
                msg="Cannot retype volume '{0}': status must be one of {1}, "
                    "but is '{2}'.".format(
                        volume.id,
                        allowed_statuses,
                        volume.status,
                    )
            )

        # ---- Check mode: report what would change without making API calls ----
        if self.ansible.check_mode:
            self.exit_json(
                changed=True,
                volume=volume.to_dict(),
            )

        # ---- Perform the retype ----
        # openstacksdk exposes retype via the block_storage proxy (SDK >= 1.x).
        # The Cinder REST action is POST /volumes/{id}/action with body:
        #   {"os-retype": {"new_type": "<type>", "migration_policy": "<policy>"}}
        self.conn.block_storage.retype_volume(
            volume.id,
            new_type=target_type.id,
            migration_policy=migration_policy,
        )

        # ---- Optionally wait ----
        if wait:
            volume = self._wait_for_retype(volume.id, migration_policy, timeout)
        else:
            volume = self.conn.block_storage.get_volume(volume.id)

        self.exit_json(
            changed=True,
            volume=volume.to_dict(),
        )


def main():
    module = VolumeRetypeModule()
    module()


if __name__ == '__main__':
    main()
