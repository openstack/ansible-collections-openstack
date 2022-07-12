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

set -e

if python -c 'import sys; sys.exit(0 if sys.version_info[0:2] < (3, 6) else 1)'; then
    echo "Skipped Ansible Galaxy content importer check because it requires Python 3.6 or later" 2>&1
    exit
fi

TOXDIR="${1:-.}"
python -m galaxy_importer.main "$TOXDIR/build_artifact/"*
