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

chmod 777 data
docker-compose up -d
wait_for_port 8081 "Flink Cluster"
wait_for_port 2181 "Zookeeper Cluster"
wait_for_port 9093 "Kafka Cluster"

python initialize_kafka_topic.py
python main.py &
export PID=$!
curl -LO https://archive.apache.org/dist/kafka/3.2.3/kafka_2.12-3.2.3.tgz
tar -xzf kafka_2.12-3.2.3.tgz

TIMEOUT_SECONDS=$((SECONDS + 120)) # timeout in 2 minutes
while true; do
  ./kafka_2.12-3.2.3/bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9093 \
    --topic user_online_features \
    --from-beginning \
    --timeout-ms 20000 > data/kafka-output
  if [ "$(wc -l < data/kafka-output)" -ge 5 ]; then
    break
  fi;

  if [ "${SECONDS}" -ge "${TIMEOUT_SECONDS}" ]; then
    echo "Timeout waiting for kafka output."
    exit 1
  fi
done

kill "${PID}"
docker-compose down

sort_and_compare_files data/kafka-output data/expected_output.txt

rm -rf kafka_2.12-3.2.3.tgz kafka_2.12-3.2.3
