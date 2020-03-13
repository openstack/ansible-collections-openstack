#!/usr/bin/env python
# Copyright 2019 Red Hat, Inc.
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

import pbr.version

from ruamel.yaml import YAML

import os
import shutil


def generate_version_info():
    version_info = pbr.version.VersionInfo('openstack-cloud')
    semantic_version = version_info.semantic_version()
    release_string = semantic_version._long_version('-')

    yaml = YAML()
    yaml.explicit_start = True
    yaml.indent(sequence=4, offset=2)

    config = yaml.load(open('galaxy.yml.in'))
    config['version'] = release_string

    with open('galaxy.yml', 'w') as fp:
        yaml.dump(config, fp)


def main():
    generate_version_info()
    shutil.rmtree('build_artifact', ignore_errors=True)
    if os.path.exists('MANIFEST.json'):
        os.unlink('MANIFEST.json')


if __name__ == '__main__':
    main()
