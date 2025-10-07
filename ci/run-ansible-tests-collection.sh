#!/bin/bash
#############################################################################
# run-ansible-tests.sh
#
# Script used to setup a tox environment for running Ansible. This is meant
# to be called by tox (via tox.ini). To run the Ansible tests, use:
#
#    tox -e ansible [TAG ...]
# or
#    tox -e ansible -- -c cloudX -u cloudY [TAG ...]
# or to use the development version of Ansible:
#    tox -e ansible -- -d -c cloudX -u cloudY [TAG ...]
#
# USAGE:
#    run-ansible-tests.sh -e ENVDIR [-d] [-c CLOUD] [-u CLOUD_ALT] [TAG ...]
#
# PARAMETERS:
#    -d            Use Ansible source repo development branch.
#    -e ENVDIR     Directory of the tox environment to use for testing.
#    -c CLOUD      Name of the cloud to use for testing.
#                  Defaults to "devstack-admin".
#    -u CLOUD_ALT  Name of another cloud to use for testing.
#                  Defaults to "devstack-alt".
#    [TAG ...]     Optional list of space-separated tags to control which
#                  modules are tested.
#
# EXAMPLES:
#    # Run all Ansible tests
#    run-ansible-tests.sh -e ansible
#
#    # Run auth, keypair, and network tests against cloudX
#    run-ansible-tests.sh -e ansible -c cloudX auth keypair network
#############################################################################
set -ex

CLOUD="devstack-admin"
CLOUD_ALT="devstack-alt"
ENVDIR=
USE_DEV=0

while getopts "c:de:u:" opt
do
    case $opt in
    d) USE_DEV=1 ;;
    c) CLOUD=$OPTARG ;;
    u) CLOUD_ALT=$OPTARG ;;
    e) ENVDIR=$OPTARG ;;
    ?) echo "Invalid option: -$OPTARG"
       exit 1;;
    esac
done

# Shift arguments read by getopts
shift $((OPTIND-1))

# Remaining arguments are Ansible tags
TAGS=$( echo "$*" | tr ' ' , )

if [ -z "$ENVDIR" ]; then
    echo "Option -e is required"
    exit 1
fi

if [ ! -d ci ]; then
    echo "Script must be run from collection's root directory"
    exit 2
fi

# Install Ansible collections before dealing with virtual environments for Ansible

# Install collections used in ci
ansible-galaxy collection install --requirements-file ci/requirements.yml

# Install this collection
if [ -z "$PIP_INSTALL" ]; then
    tox -ebuild
    ansible-galaxy collection install "$(find build_artifact/ -maxdepth 1 -name 'openstack-cloud-*')" --force
    TEST_COLLECTIONS_PATHS=${HOME}/.ansible/collections:$ANSIBLE_COLLECTIONS_PATH
else
    pip freeze | grep ansible-collections-openstack
    TEST_COLLECTIONS_PATHS=$VIRTUAL_ENV/share/ansible/collections:$ANSIBLE_COLLECTIONS_PATH
fi

# We need to source the current tox environment so that Ansible will
# be setup for the correct python environment.
source "$ENVDIR/bin/activate"

if [ "$USE_DEV" -eq 1 ]; then
    if [ -d "$ENVDIR/ansible" ]; then
        echo "Using existing Ansible source repo"
    else
        echo "Installing Ansible source repo at $ENVDIR"
        git clone --recursive https://github.com/ansible/ansible.git "$ENVDIR/ansible"
    fi
    source "$ENVDIR/ansible/hacking/env-setup"
fi

# Loop through all ANSIBLE_VAR_ environment variables to allow passing the further
for var in $(env | grep -e '^ANSIBLE_VAR_'); do
  VAR_NAME=${var%%=*} # split variable name from value
  ANSIBLE_VAR_NAME=${VAR_NAME#ANSIBLE_VAR_} # cut ANSIBLE_VAR_ prefix from variable name
  ANSIBLE_VAR_NAME=${ANSIBLE_VAR_NAME,,} # lowercase ansible variable
  ANSIBLE_VAR_VALUE=${!VAR_NAME} # Get the variable value
  ANSIBLE_VARS+="${ANSIBLE_VAR_NAME}=${ANSIBLE_VAR_VALUE} " # concat variables
done

# Discover openstacksdk version
SDK_VER=$(python -c "import openstack; print(openstack.version.__version__)")

# Choose integration tests
tag_opt=""
if [ -n "$TAGS" ]; then
    tag_opt="--tags $TAGS"
fi

if ! systemctl is-enabled devstack@o-api.service 2>&1; then
    # Skip loadbalancer tasks if Octavia is not available
    tag_opt+=" --skip-tags loadbalancer"
fi

# TODO: Replace with more robust test for Magnum availability
if [ ! -e /etc/magnum ]; then
    # Skip coe tasks if Magnum is not available
    tag_opt+=" --skip-tags coe_cluster,coe_cluster_template"
fi

if ! systemctl is-enabled devstack@m-api.service 2>&1; then
    # Skip share_type tasks if Manila is not available
    tag_opt+=" --skip-tags share_type"
fi

cd ci/

# Run tests
set -o pipefail
# shellcheck disable=SC2086
ANSIBLE_COLLECTIONS_PATH=$TEST_COLLECTIONS_PATHS ansible-playbook \
    -vvv ./run-collection.yml \
    -e "sdk_version=${SDK_VER} cloud=${CLOUD} cloud_alt=${CLOUD_ALT} ${ANSIBLE_VARS}" \
    ${tag_opt} 2>&1 | sudo tee /opt/stack/logs/test_output.log
