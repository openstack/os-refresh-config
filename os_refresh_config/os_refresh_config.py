#!/usr/bin/python
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

import argparse
import logging
import os
import sys
from subprocess import check_call, CalledProcessError

BASE_DIR = os.environ.get('OS_REFRESH_CONFIG_BASE_DIR',
                          '/opt/stack/os-config-refresh')
PHASES = ['pre-configure',
          'configure',
          'migration',
          'post-configure']


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description="""Runs through all of the phases to ensure configuration is
        applied and enabled on a machine. Will exit with an error if any phase has
        a problem. Scripts should not depend on eachother having worked properly.
        Set OS_REFRESH_CONFIG_BASE_DIR environment variable to override the default
        """)
    parser.add_argument('--print-base', default=False, action='store_true',
                        help='Print base dir and exit')
    parser.add_argument('--print-phases', default=False, action='store_true',
                        help='Print phases (tab separated) and exit')
    parser.add_argument('--list', default=False, action='store_true',
                        help='Just show what would be run')
    parser.add_argument('--log-level', default='INFO',
                        choices=['ERROR', 'WARN', 'CRITICAL', 'INFO', 'DEBUG'])
    options = parser.parse_args(argv[1:])

    if options.print_base:
        print(BASE_DIR)
        return 0

    if options.print_phases:
        print("\t".join(PHASES))
        return 0

    log = logging.getLogger('os-refresh-config')
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter('[%(asctime)s] (%(name)s) [%(levelname)s] %(message)s'))
    log.addHandler(handler)
    log.setLevel(options.log_level)

    for phase in PHASES:
        phase_dir = os.path.join(BASE_DIR, '%s.d' % phase)
        log.debug('Checking %s' % phase_dir)
        if os.path.exists(phase_dir):
            args = ['run-parts', '-v']
            if options.list:
                args.append('--list')
            args.append(phase_dir)
            try:
                log.info('Starting phase %s' % phase)
                log.debug('Running %s' % args)
                check_call(args)
                sys.stdout.flush()
                sys.stderr.flush()
                log.info('Completed phase %s' % phase)
            except CalledProcessError as e:
                log.error("during %s phase. [%s]\n" % (phase, e))
                log.error("Aborting...")
                return 1
        else:
            log.debug('No dir for phase %s' % phase)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
