#!/usr/bin/python

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2013, Benno Joy <benno@ansible.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: image
short_description: Add/Delete images from OpenStack Cloud
author: OpenStack Ansible SIG
description:
   - Add or Remove images from the OpenStack Image Repository
options:
   name:
     description:
        - The name of the image when uploading - or the name/ID of the image if deleting
     required: true
     type: str
   id:
     description:
        - The ID of the image when uploading an image
     type: str
   checksum:
     description:
        - The checksum of the image
     type: str
   disk_format:
     description:
        - The format of the disk that is getting uploaded
     default: qcow2
     choices: ['ami', 'ari', 'aki', 'vhd', 'vmdk', 'raw', 'qcow2', 'vdi', 'iso', 'vhdx', 'ploop']
     type: str
   container_format:
     description:
        - The format of the container
     default: bare
     choices: ['ami', 'aki', 'ari', 'bare', 'ovf', 'ova', 'docker']
     type: str
   owner:
     description:
        - The name or ID of the project owning the image
     type: str
     aliases: ['project']
   owner_domain:
     description:
        - The name or id of the domain the project owning the image belongs to
        - May be used to identify a unique project when providing a name to the project argument and multiple projects with such name exist
     type: str
     aliases: ['project_domain']
   min_disk:
     description:
        - The minimum disk space (in GB) required to boot this image
     type: int
   min_ram:
     description:
        - The minimum ram (in MB) required to boot this image
     type: int
   is_public:
     description:
        - Whether the image can be accessed publicly.
          Note that publicizing an image requires admin role by default.
        - Use I(visibility) instead of I(is_public),
          the latter has been deprecated.
     type: bool
     default: false
   is_protected:
     description:
        - Prevent image from being deleted
     aliases: ['protected']
     type: bool
   filename:
     description:
        - The path to the file which has to be uploaded
     type: str
   ramdisk:
     description:
        - The name of an existing ramdisk image that will be associated with this image
     type: str
   kernel:
     description:
        - The name of an existing kernel image that will be associated with this image
     type: str
   properties:
     description:
        - Additional properties to be associated with this image
     default: {}
     type: dict
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
     type: str
   tags:
     description:
       - List of tags to be applied to the image
     default: []
     type: list
     elements: str
   visibility:
     description:
       - The image visibility
     type: str
     choices: [public, private, shared, community]
   volume:
     description:
       - ID of a volume to create an image from.
       - The volume must be in AVAILABLE state.
       - Switch to module M(openstack.cloud.volume) instead of using I(volume),
         the latter has been deprecated.
     type: str
requirements:
    - "python >= 3.6"
    - "openstacksdk"

extends_documentation_fragment:
- openstack.cloud.openstack
'''

EXAMPLES = '''
# Upload an image from a local file named cirros-0.3.0-x86_64-disk.img
- openstack.cloud.image:
    auth:
      auth_url: https://identity.example.com
      username: admin
      password: passme
      project_name: admin
      openstack.cloud.identity_user_domain_name: Default
      openstack.cloud.project_domain_name: Default
    name: cirros
    container_format: bare
    disk_format: qcow2
    state: present
    filename: cirros-0.3.0-x86_64-disk.img
    kernel: cirros-vmlinuz
    ramdisk: cirros-initrd
    tags:
      - custom
    properties:
      cpu_arch: x86_64
      distro: ubuntu
'''

RETURN = '''
id:
  description: ID of the image.
  returned: On success when I(state) is 'present'.
  type: str
image:
  description: Dictionary describing the image.
  type: dict
  returned: On success when I(state) is 'present'.
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
    architecture:
      description: |
        The CPU architecture that must be supported by the hypervisor.
      returned: success
      type: str
    created_at:
      description: Image created at timestamp.
      returned: success
      type: str
    container_format:
      description: Container format of the image.
      returned: success
      type: str
    direct_url:
      description: URL to access the image file kept in external store.
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
    file:
      description: The URL for the virtual machine image file.
      returned: success
      type: str
    has_auto_disk_config:
      description: >
        If root partition on disk is automatically resized before the instance
        boots.
      returned: success
      type: bool
    hash_algo:
      description: |
        The algorithm used to compute a secure hash of the image data.
      returned: success
      type: str
    hash_value:
      description: >
        The hexdigest of the secure hash of the image data computed using the
        algorithm whose name is the value of the os_hash_algo property.
      returned: success
      type: str
    hw_cpu_cores:
      description: >
        Used to pin the virtual CPUs (vCPUs) of instances to the host's physical
        CPU cores (pCPUs).
      returned: success
      type: str
    hw_cpu_policy:
      description: The hexdigest of the secure hash of the image data.
      returned: success
      type: str
    hw_cpu_sockets:
      description: Preferred number of sockets to expose to the guest.
      returned: success
      type: str
    hw_cpu_thread_policy:
      description: >
        Defines how hardware CPU threads in a simultaneous multithreading-based
        (SMT) architecture be used.
      returned: success
      type: str
    hw_cpu_threads:
      description: |
        The preferred number of threads to expose to the guest.
      returned: success
      type: str
    hw_disk_bus:
      description: |
        Specifies the type of disk controller to attach disk devices to.
      returned: success
      type: str
    hw_machine_type:
      description: |
        Enables booting an ARM system using the specified machine type.
      returned: success
      type: str
    hw_qemu_guest_agent:
      description: >
        A string boolean, which if "true", QEMU guest agent will be exposed to
        the instance.
      returned: success
      type: str
    hw_rng_model:
      description: Adds a random-number generator device to the image's instances.
      returned: success
      type: str
    hw_scsi_model:
      description: >
        Enables the use of VirtIO SCSI (virtio-scsi) to provide block device
        access for compute instances.
      returned: success
      type: str
    hw_video_model:
      description: The video image driver used.
      returned: success
      type: str
    hw_video_ram:
      description: Maximum RAM for the video image.
      returned: success
      type: str
    hw_vif_model:
      description: Specifies the model of virtual network interface device to use.
      returned: success
      type: str
    hw_watchdog_action:
      description: >
        Enables a virtual hardware watchdog device that carries out the
        specified action if the server hangs.
      returned: success
      type: str
    hypervisor_type:
      description: The hypervisor type.
      returned: success
      type: str
    instance_type_rxtx_factor:
      description: >
        Optional property allows created servers to have a different bandwidth
        cap than that defined in the network they are attached to.
      returned: success
      type: str
    instance_uuid:
      description: >
        For snapshot images, this is the UUID of the server used to create this
        image.
      returned: success
      type: str
    is_hidden:
      description: >-
        Controls whether an image is displayed in the default image-list
        response
      returned: success
      type: bool
    is_hw_boot_menu_enabled:
      description: Enables the BIOS bootmenu.
      returned: success
      type: bool
    is_hw_vif_multiqueue_enabled:
      description: |
        Enables the virtio-net multiqueue feature.
      returned: success
      type: bool
    kernel_id:
      description: >
        The ID of an image stored in the Image service that should be used as
        the kernel when booting an AMI-style image.
      returned: success
      type: str
    locations:
      description: A list of URLs to access the image file in external store.
      returned: success
      type: str
    metadata:
      description: The location metadata.
      returned: success
      type: str
    needs_config_drive:
      description: Specifies whether the image needs a config drive.
      returned: success
      type: bool
    needs_secure_boot:
      description: Whether Secure Boot is needed.
      returned: success
      type: bool
    os_admin_user:
      description: The operating system admin username.
      returned: success
      type: str
    os_command_line:
      description: The kernel command line to be used by libvirt driver.
      returned: success
      type: str
    os_distro:
      description: |
        The common name of the operating system distribution in lowercase.
      returned: success
      type: str
    os_require_quiesce:
      description: |
        If true, require quiesce on snapshot via QEMU guest agent.
      returned: success
      type: str
    os_shutdown_timeout:
      description: Time for graceful shutdown.
      returned: success
      type: str
    os_type:
      description: The operating system installed on the image.
      returned: success
      type: str
    os_version:
      description: |
        The operating system version as specified by the distributor.
      returned: success
      type: str
    owner_id:
      description: 'The ID of the owner, or project, of the image.'
      returned: success
      type: str
    ramdisk_id:
      description: >
        The ID of image stored in the Image service that should be used as the
        ramdisk when booting an AMI-style image.
      returned: success
      type: str
    schema:
      description: URL for the schema describing a virtual machine image.
      returned: success
      type: str
    store:
      description: >
        Glance will attempt to store the disk image data in the backing store
        indicated by the value of the header.
      returned: success
      type: str
    updated_at:
      description: Image updated at timestamp.
      returned: success
      type: str
    url:
      description: URL to access the image file kept in external store.
      returned: success
      type: str
    virtual_size:
      description: The virtual size of the image.
      returned: success
      type: str
    vm_mode:
      description: The virtual machine mode.
      returned: success
      type: str
    vmware_adaptertype:
      description: |
        The virtual SCSI or IDE controller used by the hypervisor.
      returned: success
      type: str
    vmware_ostype:
      description: Operating system installed in the image.
      returned: success
      type: str
    filters:
      description: Additional properties associated with the image.
      returned: success
      type: dict
    min_disk:
      description: Min amount of disk space required for this image.
      returned: success
      type: int
    is_protected:
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
    visibility:
      description: Indicates who has access to the image.
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


class ImageModule(OpenStackModule):

    argument_spec = dict(
        name=dict(required=True, type='str'),
        id=dict(type='str'),
        checksum=dict(type='str'),
        disk_format=dict(default='qcow2',
                         choices=['ami', 'ari', 'aki', 'vhd', 'vmdk', 'raw', 'qcow2', 'vdi', 'iso', 'vhdx', 'ploop']),
        container_format=dict(default='bare', choices=['ami', 'aki', 'ari', 'bare', 'ovf', 'ova', 'docker']),
        owner=dict(type='str', aliases=['project']),
        owner_domain=dict(type='str', aliases=['project_domain']),
        min_disk=dict(type='int', default=0),
        min_ram=dict(type='int', default=0),
        is_public=dict(type='bool', default=False),
        is_protected=dict(type='bool', aliases=['protected']),
        filename=dict(type='str'),
        ramdisk=dict(type='str'),
        kernel=dict(type='str'),
        properties=dict(type='dict', default={}),
        volume=dict(type='str'),
        tags=dict(type='list', default=[], elements='str'),
        state=dict(default='present', choices=['absent', 'present']),
        visibility=dict(type='str', choices=['public', 'private', 'shared', 'community']),
    )

    module_kwargs = dict(
        mutually_exclusive=[
            ('filename', 'volume'),
            ('visibility', 'is_public'),
        ],
    )

    # resource attributes obtainable directly from params
    attr_params = ('id', 'name', 'filename', 'disk_format',
                   'container_format', 'wait', 'timeout', 'is_public',
                   'is_protected', 'min_disk', 'min_ram', 'volume', 'tags')

    def _resolve_visibility(self):
        """resolve a visibility value to be compatible with older versions"""
        if self.params['visibility']:
            return self.params['visibility']
        if self.params['is_public'] is not None:
            return 'public' if self.params['is_public'] else 'private'
        return None

    def _build_params(self, owner):
        params = {attr: self.params[attr] for attr in self.attr_params}
        if owner:
            params['owner_id'] = owner.id
        params['visibility'] = self._resolve_visibility()
        params = {k: v for k, v in params.items() if v is not None}
        return params

    def _return_value(self, image_name_or_id):
        image = self.conn.image.find_image(image_name_or_id)
        if image:
            image = image.to_dict(computed=False)
        return image

    def _build_update(self, image):
        update_payload = dict(is_protected=self.params['is_protected'])
        for k in ('kernel', 'ramdisk'):
            if not self.params[k]:
                continue
            k_id = '{0}_id'.format(k)
            k_image = self.conn.image.find_image(
                name_or_id=self.params[k], ignore_missing=False)
            update_payload[k_id] = k_image.id
        update_payload = {k: v for k, v in update_payload.items()
                          if v is not None and image[k] != v}
        for p, v in self.params['properties'].items():
            if p not in image or image[p] != v:
                update_payload[p] = v
        if (self.params['tags']
                and set(image['tags']) != set(self.params['tags'])):
            update_payload['tags'] = self.params['tags']
        return update_payload

    def run(self):
        changed = False
        image_filters = {}
        image_name_or_id = self.params['id'] or self.params['name']
        owner_name_or_id = self.params['owner']
        owner_domain_name_or_id = self.params['owner_domain']

        if self.params['checksum']:
            image_filters['checksum'] = image_filters
        owner_filters = {}
        if owner_domain_name_or_id:
            owner_domain = self.conn.identity.find_domain(
                owner_domain_name_or_id)
            if owner_domain:
                owner_filters['domain_id'] = owner_domain.id
            else:
                # else user may not be able to enumerate domains
                owner_filters['domain_id'] = owner_domain_name_or_id

        owner = None
        if owner_name_or_id:
            owner = self.conn.identity.find_project(
                owner_name_or_id, ignore_missing=False, **owner_filters)

        image = None
        if image_name_or_id:
            image = self.conn.image.find_image(image_name_or_id, **image_filters)

        changed = False
        if self.params['state'] == 'present':
            attrs = self._build_params(owner)
            if not image:
                # self.conn.image.create_image cannot be used because
                # self.conn.create_image provides a volume parameter
                # Ref.: https://opendev.org/openstack/openstacksdk/src/commit/a41d04ea197439c2f134ce3554995693933a46ac/openstack/cloud/_image.py#L306
                image = self.conn.create_image(**attrs)
                changed = True
                if not self.params['wait']:
                    self.exit_json(changed=changed,
                                   image=self._return_value(image.id),
                                   id=image.id)

            update_payload = self._build_update(image)

            if update_payload:
                self.conn.image.update_image(image, **update_payload)
                changed = True

            self.exit_json(changed=changed, image=self._return_value(image.id),
                           id=image.id)

        elif self.params['state'] == 'absent' and image is not None:
            # self.conn.image.delete_image() does not offer a wait parameter
            self.conn.delete_image(
                name_or_id=image['id'],
                wait=self.params['wait'],
                timeout=self.params['timeout'])
            changed = True
        self.exit_json(changed=changed)


def main():
    module = ImageModule()
    module()


if __name__ == '__main__':
    main()
