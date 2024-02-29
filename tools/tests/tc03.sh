#!/bin/bash
#
# Runs dib-run-parts on directory containing some scripts
# and using the environment directory.
#

set -ue
set -o pipefail
set -x

TESTS_BASE_DIR=$(dirname $0)

DRP_BIN=${TESTS_BASE_DIR}/../dib-run-parts

TEST_EXEC_DIR=${TESTS_BASE_DIR}/tc03/td

rval=0

RES=$(${DRP_BIN} ${TEST_EXEC_DIR} 2>/dev/null)
if test $? -ne 0; then
    echo "*** FAILED: dib-run-parts failed"
    rval=1
fi

EXPECTED="call_me_1 called [Some thing]
call_me_2 called [Other thing]"

if test "${EXPECTED}" != "${RES}"; then
    echo "*** FAILED: dib-run-parts returns incorrect result"
    rval=1
fi

exit ${rval}
