#!/bin/bash
#
# Runs dib-run-parts on an empty directory.
#

set -ue
set -o pipefail
set -x

TESTS_BASE_DIR=$(cd $(dirname "$0") && pwd)

DRP_BIN=${TESTS_BASE_DIR}/../dib-run-parts

TEST_EXEC_DIR=${TESTS_BASE_DIR}/tc01/td

mkdir -p ${TEST_EXEC_DIR}
rval=0

RES=$(${DRP_BIN} --list ${TEST_EXEC_DIR})
if test $? -ne 0; then
    echo "*** FAILED: --list of empty dir failed"
    rval=1
fi
if test -n "${RES}"; then
    echo "*** FAILED: --list of empty dir not empty"
    rval=1
fi

RES=$(${DRP_BIN} ${TEST_EXEC_DIR} 2>/dev/null)
if test $? -ne 0; then
    echo "*** FAILED: dib-run-parts on empty dir failed"
    rval=1
fi
if test -n "${RES}"; then
    echo "*** FAILED: dib-run-parts on empty dir not empty"
    rval=1
fi

exit ${rval}
