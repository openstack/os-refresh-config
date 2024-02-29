#!/bin/bash
#
# Runs dib-run-parts on directory containing some scripts.
#

set -ue
set -o pipefail
set -x

TESTS_BASE_DIR=$(cd $(dirname "$0") && pwd)

DRP_BIN=${TESTS_BASE_DIR}/../dib-run-parts

TEST_EXEC_DIR=${TESTS_BASE_DIR}/tc02/td

rval=0

RES=$(${DRP_BIN} --list ${TEST_EXEC_DIR})
if test $? -ne 0; then
    echo "*** FAILED: --list failed"
    rval=1
fi

EXPECTED="${TESTS_BASE_DIR}/tc02/td/call_me_1
${TESTS_BASE_DIR}/tc02/td/call_me_2"

if test "${EXPECTED}" != "${RES}"; then
    echo "*** FAILED: --list returns incorrect result"
    rval=1
fi

RES=$(${DRP_BIN} ${TEST_EXEC_DIR} 2>/dev/null)
if test $? -ne 0; then
    echo "*** FAILED: dib-run-parts on empty dir failed"
    rval=1
fi

EXPECTED="call_me_1 called
call_me_2 called"

if test "${EXPECTED}" != "${RES}"; then
    echo "*** FAILED: dib-run-parts returns incorrect result"
    rval=1
fi

exit ${rval}
