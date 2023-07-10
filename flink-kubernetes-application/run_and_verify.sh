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

eval $(minikube docker-env)
docker build -q --rm -t flink-k8s-app .
minikube ssh -- 'mkdir -p -m=777 /tmp/flink-kubernetes-application/output'
kubectl create clusterrolebinding flink-role-binding-default --clusterrole=edit --serviceaccount=default:default

curl -LO https://archive.apache.org/dist/flink/flink-1.16.2/flink-1.16.2-bin-scala_2.12.tgz
tar -xzf flink-1.16.2-bin-scala_2.12.tgz
./flink-1.16.2/bin/flink run-application \
  --target kubernetes-application \
  -Dkubernetes.container.image=flink-k8s-app:latest \
  -Dkubernetes.pod-template-file=./pod-template.yaml \
  -Dkubernetes.jobmanager.cpu=0.25 \
  -Dkubernetes.taskmanager.cpu=0.25 \
  -Djobmanager.memory.process.size=1G \
  -Dtaskmanager.memory.process.size=1G \
  -py /main.py

POD_NAME=$(kubectl get po --no-headers=true | awk '{print $1}')
kubectl wait pods --for=condition=Ready "${POD_NAME}"
kubectl logs -f "${POD_NAME}"

minikube ssh --native-ssh=false -- 'cat /tmp/flink-kubernetes-application/output/output.json/*' > data/merged_output
sort_and_compare_files data/merged_output data/expected_output.txt

rm -rf flink-1.16.2-bin-scala_2.12.tgz ./flink-1.16.2

