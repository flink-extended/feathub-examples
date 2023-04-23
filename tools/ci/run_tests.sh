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
set -e

PROJECT_DIR=$(cd "$(dirname "$0")/../.."; pwd)

python -m pip -q install --upgrade "feathub-nightly[flink]"

python -m pip -q install --upgrade "feathub-nightly[spark]"

docker build -q --rm -t feathub-flink -f ./docker/Dockerfile .

# Run the run_and_verify.sh script in each example folder
for EXAMPLE_RUN_SCRIPT in "${PROJECT_DIR}"/flink-sliding-feature-view/run_and_verify.sh; do
  echo "Running example ${EXAMPLE_RUN_SCRIPT}..."
  bash "${EXAMPLE_RUN_SCRIPT}"
  echo "Example ${EXAMPLE_RUN_SCRIPT} success."
done
