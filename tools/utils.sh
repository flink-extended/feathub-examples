#
# Copyright 2022 The FeatHub Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

function wait_for_port {
  local PORT=$1
	local COMPONENT_NAME=$2
	local TIMEOUT_SECONDS=$((SECONDS + 120)) # timeout in 2 minutes
  while ! nc -z 127.0.0.1 "${PORT}"; do
    sleep 1
    echo "Waiting for ${COMPONENT_NAME}..."
    if [ "${SECONDS}" -ge "${TIMEOUT_SECONDS}" ]; then
      echo "Timeout waiting for ${COMPONENT_NAME}."
      exit 1
    fi
  done
}

function sort_and_compare_files {
  local FILE1=$1
	local FILE2=$2

  echo "Sort and compare file ${FILE1} and ${FILE2}"
	sort "${FILE1}" > "${FILE1}".sorted

	# The return code of diff is non-zero if the files are different.
	sort "${FILE2}" | diff - "${FILE1}".sorted

	rm "${FILE1}".sorted
}