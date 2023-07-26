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

cd "$(dirname "$0")"
PROJECT_DIR=$(cd "$(pwd)/.."; pwd)
source "${PROJECT_DIR}"/tools/utils.sh

wget -nc https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-hive-3.1.2_2.12/1.16.1/flink-sql-connector-hive-3.1.2_2.12-1.16.1.jar

chmod 777 data
docker-compose up -d
wait_for_port 8081 "Flink Cluster"
sleep 20 # TODO: fix wait_for_port to check for service availability, not just connection.

docker exec -w /root/flink-read-write-hive flink bash -c "export HADOOP_CLASSPATH=\`hadoop classpath\`; python main.py" &
export PID=$!

TIMEOUT_SECONDS=$((SECONDS + 120)) # timeout in 2 minutes
while true; do
  sleep 10

  if [ "$(ls -a data/output | wc -l)" -ge 3 ]; then
    break
  fi;

  if [ "${SECONDS}" -ge "${TIMEOUT_SECONDS}" ]; then
    echo "Timeout waiting for output."
    exit 1
  fi
done

kill "${PID}"
tear_down_docker

cat data/output/.part-* > data/merged_output

sort_and_compare_files data/merged_output data/expected_output.csv
