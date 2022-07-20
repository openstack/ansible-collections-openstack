#!/usr/bin/python

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: image_info
short_description: Retrieve information about an image within OpenStack.
author: OpenStack Ansible SIG
description:
    - Retrieve information about a image image from OpenStack.
options:
   image:
     description:
        - Name or ID of the image
     required: false
     type: str
   filters:
     description:
        - Dict of properties of the images used for query
     type: dict
     required: false
     aliases: ['properties']
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
    msg: "{{ result.image }}"

# Show all available Openstack images
- name: Retrieve all available Openstack images
  openstack.cloud.image_info:
  register: result

- name: Show images
  debug:
    msg: "{{ result.image }}"

# Show images matching requested properties
- name: Retrieve images having properties with desired values
  openstack.cloud.image_facts:
    filters:
      some_property: some_value
      OtherProp: OtherVal

- name: Show images
  debug:
    msg: "{{ result.image }}"
'''

RETURN = '''
images:
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
        architecture:
            description: >
                The CPU architecture that must be supported by
                the hypervisor.
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
                If root partition on disk is automatically resized
                before the instance boots.
            returned: success
            type: bool
        hash_algo:
            description: >
                The algorithm used to compute a secure hash of the
                image data.
            returned: success
            type: str
        hash_value:
            description: >
                The hexdigest of the secure hash of the image data
                computed using the algorithm whose name is the value of the os_hash_algo property.
            returned: success
            type: str
        hw_cpu_cores:
            description: >
                Used to pin the virtual CPUs (vCPUs) of instances to
                the host's physical CPU cores (pCPUs).
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
            description:  >
                Defines how hardware CPU threads in a simultaneous
                multithreading-based (SMT) architecture be used.
            returned: success
            type: str
        hw_cpu_threads:
            description: >
                The preferred number of threads to expose to the guest.
            returned: success
            type: str
        hw_disk_bus:
            description: >
                Specifies the type of disk controller to attach disk
                devices to.
            returned: success
            type: str
        hw_machine_type:
            description: >
                Enables booting an ARM system using the
                specified machine type.
            returned: success
            type: str
        hw_qemu_guest_agent:
            description: >
                A string boolean, which if "true", QEMU guest agent
                will be exposed to the instance.
            returned: success
            type: str
        hw_rng_model:
            description: Adds a random-number generator device to the image's instances.
            returned: success
            type: str
        hw_scsi_model:
            description: >
                Enables the use of VirtIO SCSI (virtio-scsi) to
                provide block device access for compute instances.
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
                Enables a virtual hardware watchdog device that
                carries out the specified action if the server hangs.
            returned: success
            type: str
        hypervisor_type:
            description: The hypervisor type.
            returned: success
            type: str
        instance_type_rxtx_factor:
            description: >
                Optional property allows created servers to have a
                different bandwidth cap than that defined in the network they are attached to.
            returned: success
            type: str
        instance_uuid:
            description: >
                For snapshot images, this is the UUID of the server
                used to create this image.
            returned: success
            type: str
        is_hidden:
            description: Controls whether an image is displayed in the default image-list response
            returned: success
            type: bool
        is_hw_boot_menu_enabled:
            description: Enables the BIOS bootmenu.
            returned: success
            type: bool
        is_hw_vif_multiqueue_enabled:
            description: >
                Enables the virtio-net multiqueue
                feature.
            returned: success
            type: bool
        kernel_id:
            description: >
                The ID of an image stored in the Image service that
                should be used as the kernel when booting an AMI-style image.
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
            description: >
                The common name of the operating system distribution
                in lowercase.
            returned: success
            type: str
        os_require_quiesce:
            description: >
                If true, require quiesce on snapshot via
                QEMU guest agent.
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
            description: >
                The operating system version as specified by
                the distributor.
            returned: success
            type: str
        owner_id:
            description: The ID of the owner, or project, of the image.
            returned: success
            type: str
        ramdisk_id:
            description: >
                The ID of image stored in the Image service that
                should be used as the ramdisk when booting an AMI-style image.
            returned: success
            type: str
        schema:
            description: URL for the schema describing a virtual machine image.
            returned: success
            type: str
        store:
            description: >
                Glance will attempt to store the disk
                image data in the backing store indicated by the value of the
                header.
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
            description: >
                The virtual SCSI or IDE controller used by the
                hypervisor.
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


class ImageInfoModule(OpenStackModule):

    argument_spec = dict(
        image=dict(type='str', required=False),
        filters=dict(type='dict', required=False, aliases=['properties']),
    )
    module_kwargs = dict(
        supports_check_mode=True
    )

    def run(self):
        args = {
            'name_or_id': self.params['image'],
            'filters': self.params['filters'],
        }
        args = {k: v for k, v in args.items() if v is not None}
        images = [image.to_dict(computed=False) for image in
                  self.conn.search_images(**args)]
        self.exit(changed=False, images=images)


def main():
    module = ImageInfoModule()
    module()


if __name__ == '__main__':
    main()
