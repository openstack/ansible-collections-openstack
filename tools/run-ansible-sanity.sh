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

PY_VER=$(python3 -c "from platform import python_version;print(python_version())" | cut -f 1,2 -d".")
echo "Running test with Python version ${PY_VER}"

rm -rf "${ANSIBLE_COLLECTIONS_PATH}"
mkdir -p ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/openstack/cloud
cp -a ${TOXDIR}/{plugins,meta,tests,docs,galaxy.yml} ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/openstack/cloud
cd ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/openstack/cloud/
echo "Running ansible-test with version:"
ansible --version
# Ansible-core 2.17 dropped support for the metaclass-boilerplate and future-import-boilerplate tests.
# TODO(mgoddard): Drop this workaround when ansible-core 2.16 is EOL.
ANSIBLE_VER=$(python3 -m pip show ansible-core | awk '$1 == "Version:" { print $2 }')
ANSIBLE_MAJOR_VER=$(echo "$ANSIBLE_VER" | sed 's/^\([0-9]\)\..*/\1/g')
SKIP_TESTS=""
if [[ $ANSIBLE_MAJOR_VER -eq 2 ]]; then
    ANSIBLE_MINOR_VER=$(echo "$ANSIBLE_VER" | sed 's/^2\.\([^\.]*\)\..*/\1/g')
    if [[ $ANSIBLE_MINOR_VER -le 16 ]]; then
        SKIP_TESTS="--skip-test metaclass-boilerplate --skip-test future-import-boilerplate"
    fi
fi
ansible-test sanity -v \
    --venv \
    --python ${PY_VER} \
    $SKIP_TESTS \
    plugins/ docs/ meta/
