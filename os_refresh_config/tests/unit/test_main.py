# Copyright 2014 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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
import os

import fixtures
import testtools

from os_refresh_config import os_refresh_config


class TestMain(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.useFixture(fixtures.NestedTempfile())
        td = self.useFixture(fixtures.TempDir())
        self.useFixture(
            fixtures.EnvironmentVariable(
                "OS_REFRESH_CONFIG_BASE_DIR",
                td.path))

    def _run_main(self, args=[]):
        self.lockdir = self.useFixture(fixtures.TempDir())
        self.lockfile = os.path.join(self.lockdir.path, 'lock')
        return os_refresh_config.main(argv=['os-refresh-config',
                                      '--lockfile', self.lockfile])

    def test_main(self):
        self.assertEqual(0, self._run_main())
        self.assertTrue(os.path.exists(self.lockfile))
        self.assertEqual(0, len(open(self.lockfile).read()))
