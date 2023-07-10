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

curl -LO https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xzf hadoop-3.3.6.tar.gz --exclude='hadoop-3.3.6/share/doc/**' --exclude='hadoop-3.3.6/share/tools/lib/**'
rm -rf hadoop-3.3.6.tar.gz
cp -r etc/hadoop hadoop-3.3.6/etc
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
./hadoop-3.3.6/bin/hdfs namenode -format
./hadoop-3.3.6/sbin/start-dfs.sh
./hadoop-3.3.6/sbin/start-yarn.sh

echo Waiting for the Yarn cluster to be ready... sleep 30 seconds
sleep 30

echo Preparing Environment
pip -q install virtualenv
python -m virtualenv venv
source venv/bin/activate
pip -q install "feathub-nightly[flink]"
deactivate
zip -q -r venv.zip venv
./hadoop-3.3.6/bin/hdfs dfs -put venv.zip /venv.zip
rm -rf venv venv.zip
./hadoop-3.3.6/bin/hdfs dfs -put data /data
./hadoop-3.3.6/bin/hdfs dfs -put main.py /main.py

echo Submitting Feathub job to Yarn cluster
curl -LO https://archive.apache.org/dist/flink/flink-1.16.2/flink-1.16.2-bin-scala_2.12.tgz
tar -xzf flink-1.16.2-bin-scala_2.12.tgz
rm -rf flink-1.16.2-bin-scala_2.12.tgz
HADOOP_CLASSPATH=$(hadoop-3.3.6/bin/hadoop classpath) \
./flink-1.16.2/bin/flink run-application \
   -t yarn-application \
   -Dyarn.application.name=feathub_job \
   -pyarch hdfs:///venv.zip \
   -pyclientexec venv.zip/venv/bin/python3 \
   -pyexec venv.zip/venv/bin/python3 \
   -pyfs hdfs:///main.py \
   -pym main

APPLICATION_ID=$(./hadoop-3.3.6/bin/yarn app -list | grep feathub_job | awk '{print $1}')
echo Yarn Application ID: "$APPLICATION_ID"

TIMEOUT_SECONDS=$((SECONDS + 120)) # timeout in 2 minutes
STATE=$(./hadoop-3.3.6/bin/yarn app -status "$APPLICATION_ID" | grep State | grep -v "Final" | awk -F ' : ' '{print $2}')
while [[ $STATE != "FINISHED" ]]; do
  sleep 5
  echo "Waiting for ${APPLICATION_ID} FINISH... Current State: ${STATE}"
  STATE=$(./hadoop-3.3.6/bin/yarn app -status "$APPLICATION_ID" | grep State | grep -v "Final" | awk -F ' : ' '{print $2}')
  if [ "${SECONDS}" -ge "${TIMEOUT_SECONDS}" ]; then
    echo "Timeout waiting for ${APPLICATION_ID} FINISH..."
    exit 1
  fi
done

FINAL_STATE=$(./hadoop-3.3.6/bin/yarn app -status "$APPLICATION_ID" | grep Final-State | awk -F ' : ' '{print $2}')
echo "Final State of job ${APPLICATION_ID} is: ${FINAL_STATE}"
if [[ $FINAL_STATE != "SUCCEEDED" ]]; then
  exit 1
fi

./hadoop-3.3.6/bin/hdfs dfs -get /data/output.json data/output.json

cat data/output.json/* > data/merged_output
sort_and_compare_files data/merged_output data/expected_output.txt

./hadoop-3.3.6/sbin/stop-yarn.sh
./hadoop-3.3.6/sbin/stop-dfs.sh

rm -rf hadoop-3.3.6 flink-1.16.2
