#!/bin/bash
# Copyright 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

TOXDIR=${1:-.}
ANSIBLE_COLLECTIONS_PATH=$(mktemp -d)
echo "Executing ansible-test sanity checks in ${ANSIBLE_COLLECTIONS_PATH}"

trap "rm -rf ${ANSIBLE_COLLECTIONS_PATH}" err exit

rm -rf "${ANSIBLE_COLLECTIONS_PATH}"
mkdir -p ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/openstack/cloud
cp -a ${TOXDIR}/{plugins,meta,scripts,tests,docs} ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/openstack/cloud
cd ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/openstack/cloud/
ansible-test sanity -v \
    --skip-test metaclass-boilerplate \
    --skip-test future-import-boilerplate \
    plugins/ docs/ meta/ scripts/ tests/
