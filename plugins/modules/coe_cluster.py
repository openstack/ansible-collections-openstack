#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Catalyst IT Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: coe_cluster
short_description: Manage COE cluster in OpenStack Cloud
author: OpenStack Ansible SIG
description:
  - Add or remove a COE (Container Orchestration Engine) cluster
    via OpenStack's Magnum aka Container Infrastructure Management API.
options:
  cluster_template_id:
    description:
      - The template ID of cluster template.
      - Required if I(state) is C(present).
    type: str
  discovery_url:
    description:
      - URL used for cluster node discovery.
    type: str
  docker_volume_size:
    description:
      - The size in GB of the docker volume.
    type: int
  flavor_id:
    description:
      - The flavor of the minion node for this cluster template.
    type: str
  floating_ip_enabled:
    description:
      - Indicates whether created cluster should have a floating ip.
      - Whether enable or not using the floating IP of cloud provider. Some
        cloud providers used floating IP, some used public IP, thus Magnum
        provide this option for specifying the choice of using floating IP.
      - If not set, the value of I(floating_ip_enabled) of the cluster template
        specified with I(cluster_template_id) will be used.
      - When I(floating_ip_enabled) is set to C(true), then
        I(external_network_id) in cluster template must be defined.
    type: bool
  keypair:
    description:
      - Name of the keypair to use.
    type: str
  labels:
    description:
      - One or more key/value pairs.
    type: raw
  master_count:
    description:
      - The number of master nodes for this cluster.
      - Magnum's default value for I(master_count) is 1.
    type: int
  master_flavor_id:
    description:
      - The flavor of the master node for this cluster template.
    type: str
  name:
    description:
      - Name that has to be given to the cluster template.
    required: true
    type: str
  node_count:
    description:
      - The number of nodes for this cluster.
      - Magnum's default value for I(node_count) is 1.
    type: int
  state:
    description:
      - Indicate desired state of the resource.
    choices: [present, absent]
    default: present
    type: str
notes:
  - Return values of this module are preliminary and will most likely change
    when openstacksdk has finished its transition of cloud layer functions to
    resource proxies.
requirements:
  - "python >= 3.6"
  - "openstacksdk"
extends_documentation_fragment:
  - openstack.cloud.openstack
'''

# TODO: Update return values when coe related functions in openstacksdk
#       have been ported to resource proxies.
RETURN = r'''
cluster:
  description: Dictionary describing the cluster.
  returned: On success when I(state) is C(present).
  type: complex
  contains:
    cluster_template_id:
      description: The cluster_template UUID
      type: str
      sample: '7b1418c8-cea8-48fc-995d-52b66af9a9aa'
    create_timeout:
      description: Timeout for creating the cluster in minutes.
                   Default to 60 if not set.
      type: int
      sample: 60
    id:
      description: Unique UUID for this cluster.
      type: str
      sample: '86246a4d-a16c-4a58-9e96ad7719fe0f9d'
    keypair:
      description: Name of the keypair to use.
      type: str
      sample: mykey
    location:
      description: The OpenStack location of this resource.
      type: str
    master_count:
      description: The number of master nodes for this cluster.
      type: int
      sample: 1
    name:
      description: Name that has to be given to the cluster.
      type: str
      sample: k8scluster
    node_count:
      description: The number of master nodes for this cluster.
      type: int
      sample: 1
    properties:
      description: Additional properties of the cluster template.
      type: dict
      sample: |
        {
          'api_address': 'https://172.24.4.30:6443',
          'coe_version': 'v1.11.1',
          'container_version': '1.12.6',
          'created_at': '2018-08-16T10:29:45+00:00',
          'discovery_url': 'https://discovery.etcd.io/a42...aae5',
          'faults': {'0': 'ResourceInError: resources[0].resources...'},
          'flavor_id': 'c1.c1r1',
          'floating_ip_enabled': true,
          'labels': {'key1': 'value1', 'key2': 'value2'},
          'master_addresses': ['172.24.4.5'],
          'master_flavor_id': 'c1.c1r1',
          'node_addresses': ['172.24.4.8'],
          'status_reason': 'Stack CREATE completed successfully',
          'updated_at': '2018-08-16T10:39:25+00:00',
        }
    stack_id:
      description: Stack id of the Heat stack.
      type: str
      sample: '07767ec6-85f5-44cb-bd63-242a8e7f0d9d'
    status:
      description: Status of the cluster from the heat stack.
      type: str
      sample: 'CREATE_COMLETE'
    uuid:
      description: Unique UUID for this cluster.
      type: str
      sample: '86246a4d-a16c-4a58-9e96ad7719fe0f9d'
'''

EXAMPLES = r'''
- name: Create a new Kubernetes cluster
  openstack.cloud.coe_cluster:
    cloud: devstack
    cluster_template_id: k8s-ha
    keypair: mykey
    master_count: 3
    name: k8s
    node_count: 5
'''

from ansible_collections.openstack.cloud.plugins.module_utils.openstack import OpenStackModule


class COEClusterModule(OpenStackModule):
    argument_spec = dict(
        cluster_template_id=dict(),
        discovery_url=dict(),
        docker_volume_size=dict(type='int'),
        flavor_id=dict(),
        floating_ip_enabled=dict(type='bool'),
        keypair=dict(no_log=False),  # := noqa no-log-needed
        labels=dict(type='raw'),
        master_count=dict(type='int'),
        master_flavor_id=dict(),
        name=dict(required=True),
        node_count=dict(type='int'),
        state=dict(default='present', choices=['absent', 'present']),
    )
    module_kwargs = dict(
        required_if=[
            ('state', 'present', ('cluster_template_id',))
        ],
        supports_check_mode=True,
    )

    def run(self):
        state = self.params['state']

        cluster = self._find()

        if self.ansible.check_mode:
            self.exit_json(changed=self._will_change(state, cluster))

        if state == 'present' and not cluster:
            # Create cluster
            cluster = self._create()
            self.exit_json(changed=True,
                           # TODO: Add .to_dict(computed=False) when Munch
                           #       object has been replaced with openstacksdk
                           #       resource object.
                           cluster=cluster)

        elif state == 'present' and cluster:
            # Update cluster
            update = self._build_update(cluster)
            if update:
                cluster = self._update(cluster, update)

            self.exit_json(changed=bool(update),
                           # TODO: Add .to_dict(computed=False) when Munch
                           #       object has been replaced with openstacksdk
                           #       resource object.
                           cluster=cluster)

        elif state == 'absent' and cluster:
            # Delete cluster
            self._delete(cluster)
            self.exit_json(changed=True)

        elif state == 'absent' and not cluster:
            # Do nothing
            self.exit_json(changed=False)

    def _build_update(self, cluster):
        update = {}

        # TODO: Implement support for updates.
        non_updateable_keys = [k for k in ['cluster_template_id',
                                           'discovery_url',
                                           'docker_volume_size', 'flavor_id',
                                           'floating_ip_enabled', 'keypair',
                                           'master_count', 'master_flavor_id',
                                           'name', 'node_count']
                               if self.params[k] is not None
                               and self.params[k] != cluster[k]]

        labels = self.params['labels']
        if labels is not None:
            if isinstance(labels, str):
                labels = dict([tuple(kv.split(":"))
                               for kv in labels.split(",")])
            if labels != cluster['labels']:
                non_updateable_keys.append('labels')

        if non_updateable_keys:
            self.fail_json(msg='Cannot update parameters {0}'
                               .format(non_updateable_keys))

        attributes = dict((k, self.params[k])
                          for k in []
                          if self.params[k] is not None
                          and self.params[k] != cluster[k])

        if attributes:
            update['attributes'] = attributes

        return update

    def _create(self):
        # TODO: Complement *_id parameters with find_* functions to allow
        #       specifying names in addition to IDs.
        kwargs = dict((k, self.params[k])
                      for k in ['cluster_template_id', 'discovery_url',
                                'docker_volume_size', 'flavor_id',
                                'floating_ip_enabled', 'keypair',
                                'master_count', 'master_flavor_id',
                                'name', 'node_count']
                      if self.params[k] is not None)

        labels = self.params['labels']
        if labels is not None:
            if isinstance(labels, str):
                labels = dict([tuple(kv.split(":"))
                               for kv in labels.split(",")])
            kwargs['labels'] = labels

        kwargs['create_timeout'] = self.params['timeout']

        # TODO: Replace with self.conn.container_infrastructure_management.\
        #       create_cluster() when available in openstacksdk.
        cluster = self.conn.create_coe_cluster(**kwargs)

        if not self.params['wait']:
            # openstacksdk's create_coe_cluster() returns a cluster's uuid only
            # but we cannot use self.conn.get_coe_cluster(cluster_id) because
            # it might return None as long as the cluster is being set up.
            return cluster

        cluster_id = cluster['id']

        if self.params['wait']:
            # TODO: Replace with self.sdk.resource.wait_for_status() when
            #       resource creation has been ported to self.conn.\
            #       container_infrastructure_management.create_cluster()
            for count in self.sdk.utils.iterate_timeout(
                timeout=self.params['timeout'],
                message="Timeout waiting for cluster to be present"
            ):
                # Fetch cluster again
                cluster = self.conn.get_coe_cluster(cluster_id)

                if cluster is None:
                    continue
                elif cluster.status.lower() == 'active':
                    break
                elif cluster.status.lower() in ['error']:
                    self.fail_json(msg="{0} transitioned to failure state {1}"
                                       .format(cluster.name, 'error'))

        return cluster

    def _delete(self, cluster):
        # TODO: Replace with self.conn.container_infrastructure_management.\
        #       delete_cluster() when available in openstacksdk.
        self.conn.delete_coe_cluster(cluster.name)

        # TODO: Replace with self.sdk.resource.wait_for_delete() when
        #       resource fetch has been ported to self.conn.\
        #       container_infrastructure_management.find_cluster()
        if self.params['wait']:
            for count in self.sdk.utils.iterate_timeout(
                timeout=self.params['timeout'],
                message="Timeout waiting for cluster to be absent"
            ):
                cluster = self.conn.get_coe_cluster(cluster.id)
                if cluster is None:
                    break
                elif cluster['status'].lower() == 'deleted':
                    break

    def _find(self):
        name = self.params['name']
        filters = {}

        cluster_template_id = self.params['cluster_template_id']
        if cluster_template_id is not None:
            filters['cluster_template_id'] = cluster_template_id

        # TODO: Replace with self.conn.container_infrastructure_management.\
        #       find_cluster() when available in openstacksdk.
        return self.conn.get_coe_cluster(name_or_id=name, filters=filters)

    def _update(self, cluster, update):
        attributes = update.get('attributes')
        if attributes:
            # TODO: Implement support for updates.
            # TODO: Replace with self.conn.\
            #       container_infrastructure_management.\
            #       update_cluster() when available in openstacksdk.
            # cluster = self.conn.update_coe_cluster(...)
            pass

        return cluster

    def _will_change(self, state, cluster):
        if state == 'present' and not cluster:
            return True
        elif state == 'present' and cluster:
            return bool(self._build_update(cluster))
        elif state == 'absent' and cluster:
            return True
        else:
            # state == 'absent' and not cluster:
            return False


def main():
    module = COEClusterModule()
    module()


if __name__ == "__main__":
    main()
