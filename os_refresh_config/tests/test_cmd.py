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
import subprocess
import time

import fixtures
import testtools

script_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../os_refresh_config.py')


class TestCmd(testtools.TestCase):

    def setUp(self):
        super(TestCmd, self).setUp()
        self.assertTrue(os.path.exists(script_path))
        self.useFixture(fixtures.NestedTempfile())
        self.base_dir = self.useFixture(fixtures.TempDir())
        self.lockdir = self.useFixture(fixtures.TempDir())
        self.lockfile = os.path.join(self.lockdir.path, 'lock')

    def _run_cmd(self, args, env={}, input_str=None):
        subproc = subprocess.Popen(args,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=env)
        stdout, stderr = subproc.communicate(input=input_str)
        return (subproc.returncode,
                stdout.decode('utf-8'),
                stderr.decode('utf-8'))

    def _run_orc(self, *args):
        cmd_env = {
            'OS_REFRESH_CONFIG_BASE_DIR': self.base_dir.path,
            'PATH': os.environ.get('PATH')
        }
        cmd_args = [
            script_path,
            '--lockfile', self.lockfile
        ]
        if args:
            cmd_args.extend(args)
        return self._run_cmd(cmd_args, cmd_env)

    def _write_script(self, phase, name, returncode=0, sleep=0):
        phase_dir_name = '%s.d' % phase
        phase_dir = self.base_dir.join(phase_dir_name)
        if not os.path.exists(phase_dir):
            os.mkdir(phase_dir)
        script_path = self.base_dir.join(phase_dir_name, name)
        script_dict = {
            'name': name,
            'returncode': returncode,
            'sleep': sleep
        }
        with open(script_path, 'w') as f:
            f.write('''#!/bin/sh
echo %(name)s starting
sleep %(sleep)s
echo %(name)s done
exit %(returncode)s
''' % script_dict)
        os.chmod(script_path, 0o755)

    def test_cmd(self):
        returncode, stdout, stderr = self._run_orc()
        self.assertEqual(0, returncode)
        self.assertEqual('', stdout)
        self.assertEqual('', stderr)

    def test_cmd_with_scripts(self):
        self._write_script('pre-configure', '10-pre-first', 0, 0)
        self._write_script('pre-configure', '20-pre-second', 0, 1)
        self._write_script('configure', '10-conf-first', 0, 0)
        self._write_script('configure', '20-conf-second', 0, 1)
        self._write_script('post-configure', '10-post-first', 0, 0)
        self._write_script('post-configure', '20-post-second', 0, 1)
        now = time.time()
        returncode, stdout, stderr = self._run_orc()

        # check run time accounts for the 3 seconds of sleep
        self.assertTrue(time.time() - now >= 3.0)
        self.assertEqual('\n'.join([
            '10-pre-first starting',
            '10-pre-first done',
            '20-pre-second starting',
            '20-pre-second done',
            '10-conf-first starting',
            '10-conf-first done',
            '20-conf-second starting',
            '20-conf-second done',
            '10-post-first starting',
            '10-post-first done',
            '20-post-second starting',
            '20-post-second done',
            '',
        ]), stdout)
        self.assertEqual(0, returncode)

    def test_cmd_with_failure(self):
        self._write_script('pre-configure', '10-pre-first', 0)
        self._write_script('pre-configure', '20-pre-second', 99)
        self._write_script('configure', '10-conf-first', 0)
        returncode, stdout, stderr = self._run_orc()
        self.assertEqual('\n'.join([
            '10-pre-first starting',
            '10-pre-first done',
            '20-pre-second starting',
            '20-pre-second done',
            '',
        ]), stdout)
        self.assertEqual(1, returncode)

    def test_cmd_with_timeout(self):
        self._write_script('pre-configure', '10-pre-first', 0, 5)
        self._write_script('pre-configure', '20-pre-second', 0, 5)
        self._write_script('configure', '10-conf-first', 0, 5)

        now = time.time()
        returncode, stdout, stderr = self._run_orc('--timeout', '2',
                                                   '--log-level', 'DEBUG')
        # check run time accounts for the 2 seconds timeout
        self.assertTrue(time.time() - now >= 2.0)
        self.assertEqual('\n'.join([
            '10-pre-first starting',
            '',
        ]), stdout)
        self.assertEqual(1, returncode)

    def test_debug(self):
        returncode, stdout, stderr = self._run_orc('--log-level', 'DEBUG')
        self.assertEqual('', stdout)
        self.assertNotEqual('', stderr)
        self.assertEqual(0, returncode)

    def test_print_phases(self):
        returncode, stdout, stderr = self._run_orc('--print-phases')
        self.assertEqual(
            'pre-configure\tconfigure\tpost-configure\tmigration\n',
            stdout
        )
        self.assertEqual('', stderr)
        self.assertEqual(0, returncode)

    def test_print_base(self):
        returncode, stdout, stderr = self._run_orc('--print-base')
        self.assertEqual('%s\n' % self.base_dir.path, stdout)
        self.assertEqual('', stderr)
        self.assertEqual(0, returncode)
