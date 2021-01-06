#!/bin/bash

script="${BASH_SOURCE[0]}"
all_script=$(basename ${script})
test_scripts_dir=$(dirname "${BASH_SOURCE[0]}")
for i in $(ls ${test_scripts_dir}); do
    echo "Script: '${i}'"
    if [[ ${i} != ${all_script} ]]; then
        echo "Running test: ${i}"
        ${test_scripts_dir}/${i}
    fi
done
