# Overview

This example shows how to use `DerivedFeatureView` to backfill the input dataset
with extra features for offline training. It involves the following steps:

1. Read a batch of historical purchase events from a file.

   Each purchase event has the following fields:
   - user_id, unique identifier of the user that made the purchase.
   - item_id, unique identifier of the item that is purchased.
   - item_count, number of items purchased.
   - timestamp, time when this purchase is made.

2. Read a batch of historical item price events from a file.

   Each item price event has the following fields:
   - item_id, unique identifier of the item.
   - price, the new price of this item.
   - timestamp, time when the new price is used for this item.

3. For each purchase event, append the following two fields by joining with item
   price events and performing over-window aggregation, with point-in-time
   correctness in both operations.

   - price, price of the item at the time this purchase is made.
   - total_payment_last_two_minutes, total cost of purchases made by this
     user in a 2-minute window that ends at the time this purchase is made.

4. Output the batch of purchase events backfilled with the extra features to a
   file.

The example demonstrate how to submit the Feathub job to a Kubernetes cluster in Flink
native Kubernetes application mode.

# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7
- Minikube 1.30.1
- kubectl 1.25.9

# Step-By-Step Instructions

Please execute the following commands under the `flink-kubernetes-application`
folder to run this example.

1. Start the Minikube

   ```bash
   $ minikube start
   ```
   
   After the Minikube started, you can run `kubectl get ns` to see the namespace in
   the cluster.

2. Build the Flink image
   
   Flink Kubernetes application mode requires that the user code is bundle together with
   Flink image. And we need to install Feathub in the image. You can run the following
   command to build the image to be used by Minikube.

   ```bash
   eval $(minikube docker-env)
   docker build -q --rm -t flink-k8s-app .
   ```

3. Submit the Feathub job to Kubernetes cluster

   ```bash
   # Create the output directory in the Minikube.
   $ minikube ssh -- 'mkdir -p -m=777 /tmp/flink-kubernetes-application/output'
   
   # Grant the default service account with permission to create, delete pods.
   $ kubectl create clusterrolebinding flink-role-binding-default --clusterrole=edit --serviceaccount=default:default
   
   $ curl -LO https://archive.apache.org/dist/flink/flink-1.16.2/flink-1.16.2-bin-scala_2.12.tgz
   $ tar -xzf flink-1.16.2-bin-scala_2.12.tgz
   $ ./flink-1.16.2/bin/flink run-application \
       --target kubernetes-application \
       -Dkubernetes.container.image=flink-k8s-app:latest \
       -Dkubernetes.pod-template-file=./pod-template.yaml \
       -py /main.py
   ```
   
   Once the job is submitted, you can list the pod that runs the Flink JobManager and
   check out the log.
   
   ```bash
   # List the running pod.
   $ kubectl get pod
   
   $ kubectl logs <pod-name> 
   ```

4. Checkout the outputs.

   ```bash
   $ minikube ssh -- 'cat /tmp/flink-kubernetes-application/output/output.json/*'
   ```

   The file should contain the following rows:

   ```
   user_1,item_1,1,"2022-01-01 00:00:00",100.0,100.0
   user_1,item_2,2,"2022-01-01 00:01:00",200.0,500.0
   user_1,item_1,3,"2022-01-01 00:02:00",200.0,1100.0
   user_2,item_1,1,"2022-01-01 00:03:00",300.0,300.0
   user_1,item_3,2,"2022-01-01 00:04:00",300.0,1200.0
   ```

5. Tear down the Minikube.

   ```bash
   minikube stop
   ```
