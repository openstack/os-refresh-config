# Copyright 2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

import testtools

from os_refresh_config import os_refresh_config


class TestRefreshConfig(testtools.TestCase):
    def test_default_base_dir(self):
        default = '/usr/libexec/os-refresh-config'
        with mock.patch('os.path.isdir', lambda x: x == default):
            self.assertEqual(default, os_refresh_config.default_base_dir())

    def test_default_base_dir_deprecated(self):
        default = '/opt/stack/os-config-refresh'
        with mock.patch('os.path.isdir', lambda x: x == default):
            self.assertEqual(default, os_refresh_config.default_base_dir())

    def test_default_base_dir_both(self):
        default = '/usr/libexec/os-refresh-config'
        deprecated = '/opt/stack/os-config-refresh'
        with mock.patch('os.path.isdir', lambda x: (x == default or
                                                    x == deprecated)):
            self.assertEqual(default, os_refresh_config.default_base_dir())
