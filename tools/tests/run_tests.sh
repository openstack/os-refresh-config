#!/bin/bash
#
# Runs all test cases in this directory
#

set -ue
set -o pipefail

TESTS_BASE_DIR=$(cd $(dirname "$0") && pwd)

for tc in ${TESTS_BASE_DIR}/tc??.sh; do
    echo "--- Running ${tc} ---"
    ${tc}
done

echo "--- TESTS COMPLETE ---"
