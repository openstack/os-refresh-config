#!/usr/bin/env python
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
import fcntl
import logging
import os
import signal
import subprocess
import sys
import time

import psutil

OLD_BASE_DIR = '/opt/stack/os-config-refresh'
DEFAULT_BASE_DIR = '/usr/libexec/os-refresh-config'


def default_base_dir():
    """Determine the default base directory path

    If the OS_REFRESH_CONFIG_BASE_DIR environment variable is set,
    use its value.
    Otherwise, prefer the new default path, but still allow the old one for
    backwards compatibility.
    """
    base_dir = os.environ.get('OS_REFRESH_CONFIG_BASE_DIR')
    if base_dir is None:
        # NOTE(bnemec): Prefer the new location, but still allow the old one.
        if os.path.isdir(OLD_BASE_DIR) and not os.path.isdir(DEFAULT_BASE_DIR):
            logging.warning('Base directory %s is deprecated. The recommended '
                            'base directory is %s',
                            OLD_BASE_DIR, DEFAULT_BASE_DIR)
            base_dir = OLD_BASE_DIR
        else:
            base_dir = DEFAULT_BASE_DIR
    return base_dir


BASE_DIR = default_base_dir()

PHASES = ['pre-configure',
          'configure',
          'post-configure',
          'migration']


def timeout():
    p = psutil.Process()
    children = list(p.get_children(recursive=True))
    for child in children:
        child.kill()


def exit(lock, statuscode=0):
    signal.alarm(0)
    if lock:
        lock.truncate(0)
        lock.close()
    return statuscode


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description="""Runs through all of the phases to ensure
        configuration is applied and enabled on a machine. Will exit with
        an error if any phase has a problem. Scripts should not depend on
        eachother having worked properly. Set OS_REFRESH_CONFIG_BASE_DIR
        environment variable to override the default
        """)
    parser.add_argument('--print-base', default=False, action='store_true',
                        help='Print base dir and exit')
    parser.add_argument('--print-phases', default=False, action='store_true',
                        help='Print phases (tab separated) and exit')
    parser.add_argument('--log-level', default='INFO',
                        choices=['ERROR', 'WARN', 'CRITICAL', 'INFO', 'DEBUG'])
    parser.add_argument('--lockfile',
                        default='/var/run/os-refresh-config.lock',
                        help='Lock file to prevent multiple running copies.')
    parser.add_argument('--timeout',
                        type=int,
                        help='Seconds until the current run will be '
                             'terminated.')
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
        logging.Formatter(
            '[%(asctime)s] (%(name)s) [%(levelname)s] %(message)s'))
    log.addHandler(handler)
    log.setLevel(options.log_level)

    # Keep open (and thus, locked) for duration of program
    lock = open(options.lockfile, 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as e:
        log.error('Could not lock %s. %s' % (options.lockfile, e))
        return e.errno

    lock.truncate(0)
    lock.write("Locked by pid==%d at %s\n" % (os.getpid(), time.localtime()))

    def timeout_handler(signum, frame):
        log.error('Timeout reached: %ss. Sending SIGKILL to all children' %
                  options.timeout)
        timeout()

    if options.timeout:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(options.timeout)

    for phase in PHASES:
        phase_dir = os.path.join(BASE_DIR, '%s.d' % phase)
        log.debug('Checking %s' % phase_dir)
        if os.path.exists(phase_dir):
            args = ['dib-run-parts']
            args.append(phase_dir)
            try:
                log.info('Starting phase %s' % phase)
                log.debug('Running %s' % args)
                subprocess.check_call(args, close_fds=True)
                sys.stdout.flush()
                sys.stderr.flush()
                log.info('Completed phase %s' % phase)
            except subprocess.CalledProcessError as e:
                log.error("during %s phase. [%s]\n" % (phase, e))
                error_dir = os.path.join(BASE_DIR, 'error.d')
                if os.path.exists(error_dir):
                    log.info('Calling error handlers.')
                    try:
                        subprocess.call(['dib-run-parts', error_dir])
                    except OSError:
                        pass
                log.error("Aborting...")
                return exit(lock, 1)
        else:
            log.debug('No dir for phase %s' % phase)

    return exit(lock)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
