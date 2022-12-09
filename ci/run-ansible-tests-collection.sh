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
    c) CLOUD=${OPTARG} ;;
    u) CLOUD_ALT=${OPTARG} ;;
    e) ENVDIR=${OPTARG} ;;
    ?) echo "Invalid option: -${OPTARG}"
       exit 1;;
    esac
done

if [ -z ${ENVDIR} ]
then
    echo "Option -e is required"
    exit 1
fi

shift $((OPTIND-1))
TAGS=$( echo "$*" | tr ' ' , )

# Install collections before dealing with Ansible virtual environments
if [[ -z "$PIP_INSTALL" ]]; then
    tox -ebuild
    ansible-galaxy collection install $(ls build_artifact/openstack-cloud-*) --force
    TEST_COLLECTIONS_PATHS=${HOME}/.ansible/collections:$ANSIBLE_COLLECTIONS_PATHS
else
    pip freeze | grep ansible-collections-openstack
    TEST_COLLECTIONS_PATHS=$VIRTUAL_ENV/share/ansible/collections:$ANSIBLE_COLLECTIONS_PATHS
fi

# We need to source the current tox environment so that Ansible will
# be setup for the correct python environment.
source $ENVDIR/bin/activate

if [ ${USE_DEV} -eq 1 ]
then
    if [ -d ${ENVDIR}/ansible ]
    then
        echo "Using existing Ansible source repo"
    else
        echo "Installing Ansible source repo at $ENVDIR"
        git clone --recursive https://github.com/ansible/ansible.git ${ENVDIR}/ansible
    fi
    source $ENVDIR/ansible/hacking/env-setup
fi

# Run the shade Ansible tests
tag_opt=""
if [ ! -z ${TAGS} ]
then
    tag_opt="--tags ${TAGS}"
fi

# Loop through all ANSIBLE_VAR_ environment variables to allow passing the further
for var in $(env | grep -e '^ANSIBLE_VAR_'); do
  VAR_NAME=${var%%=*} # split variable name from value
  ANSIBLE_VAR_NAME=${VAR_NAME#ANSIBLE_VAR_} # cut ANSIBLE_VAR_ prefix from variable name
  ANSIBLE_VAR_NAME=${ANSIBLE_VAR_NAME,,} # lowercase ansible variable
  ANSIBLE_VAR_VALUE=${!VAR_NAME} # Get the variable value
  ANSIBLE_VARS+="${ANSIBLE_VAR_NAME}=${ANSIBLE_VAR_VALUE} " # concat variables
done

# Until we have a module that lets us determine the image we want from
# within a playbook, we have to find the image here and pass it in.
# We use the openstack client instead of nova client since it can use clouds.yaml.
IMAGE=`openstack --os-cloud=${CLOUD} image list -f value -c Name | grep cirros | grep -v -e ramdisk -e kernel`
if [ $? -ne 0 ]
then
  echo "Failed to find Cirros image"
  exit 1
fi

# In case of Octavia enabled:
_octavia_image_path="/tmp/test-only-amphora-x64-haproxy-ubuntu-bionic.qcow2"
if systemctl list-units --full -all | grep -Fq "devstack@o-api.service" && \
  test -f "$_octavia_image_path"
then
    # Upload apmhora image for Octavia to test load balancers
    OCTAVIA_AMP_IMAGE_FILE=${OCTAVIA_AMP_IMAGE_FILE:-"$_octavia_image_path"}
    OCTAVIA_AMP_IMAGE_NAME=${OCTAVIA_AMP_IMAGE_NAME:-"test-only-amphora-x64-haproxy-ubuntu-bionic"}
    OCTAVIA_AMP_IMAGE_SIZE=${OCTAVIA_AMP_IMAGE_SIZE:-3}
    openstack --os-cloud=${CLOUD} image create \
        --container-format bare \
        --disk-format qcow2 \
        --private \
        --file $OCTAVIA_AMP_IMAGE_FILE \
        --project service $OCTAVIA_AMP_IMAGE_NAME
    openstack --os-cloud=${CLOUD} image set --tag amphora $OCTAVIA_AMP_IMAGE_NAME
    # End of Octavia preparement
else
    tag_opt="$tag_opt --skip-tags loadbalancer"
fi

# Discover openstackSDK version
SDK_VER=$(python -c "import openstack; print(openstack.version.__version__)")
pushd ci/
# run tests
set -o pipefail
ANSIBLE_COLLECTIONS_PATHS=$TEST_COLLECTIONS_PATHS ansible-playbook \
    -vvv ./run-collection.yml \
    -e "sdk_version=${SDK_VER} cloud=${CLOUD} cloud_alt=${CLOUD_ALT} image=${IMAGE} ${ANSIBLE_VARS}" \
    ${tag_opt} 2>&1 | sudo tee /opt/stack/logs/test_output.log
popd
