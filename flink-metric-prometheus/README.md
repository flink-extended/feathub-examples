# Overview

This example shows how to define and export application-level metrics for
features computed by FeatHub to a Prometheus PushGateway. It involves the
following steps:

1. Read a stream of real-time purchase events from a Kafka topic.

   Each purchase event has the following fields:
   - user_id, unique identifier of the user that made the purchase.
   - item_id, unique identifier of the item that is purchased.
   - price, the price of this item by the time the purchase is made.
   - item_count, number of items purchased.
   - timestamp, time when this purchase is made.

2. For each purchase event, compute the total cost of payment made in this
   purchase event and append it to the event as a new feature.
   - Along with this feature, compute the number and proportion of large
     payments (> 500) and report these metrics to a Prometheus PushGateway.

3. Output the purchase events with the total cost features somewhere. As this is
   not the focus of this example, the results are simply discarded.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-metric-prometheus` folder
to run this example.

1. Install FeatHub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[flink]"
   ```

2. Start the Flink, Kafka cluster and Prometheus PushGateway.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink cluster has started, you should be able to navigate to the
   web UI at [localhost:8081](http://localhost:8081) to view the Flink
   dashboard.

   You may also navigate to
   [localhost:9091/metrics](http://localhost:9091/metrics) to see all the
   metrics that has been reported to the Prometheus PushGateway. There should
   have been some metrics reported by the pushgateway itself.

3. Produce events into the Kafka topic.

   ```bash
   $ python initialize_kafka_topic.py
   ```

4. Run the FeatHub program to compute the payment features and to report metrics
   to the gateway.

   ```bash
   $ python main.py
   ```

5. Checkout the metrics. Apart from the metrics that have been reported since
   the pushgateway started, you may find the following additional metrics
   reported by the Feathub program:

   ```bash
   $ curl http://localhost:9091/metrics | grep custom_namespace_total_payment | grep -v "#"
   custom_namespace_total_payment_count{feature_name="total_payment",filter_expr="> 500",instance="",job="custom_namespace",metric_type="count",table_name="",window_time_sec="86400"} 2
   custom_namespace_total_payment_ratio{feature_name="total_payment",filter_expr="> 500",instance="",job="custom_namespace",metric_type="ratio",table_name="",window_time_sec="0"} 0.4
   ```

   These metrics show that
   - 2 of the purchase events processed in the last day have their total
     payments larger than 500.
   - 40% of the purchase events processed so far have their total payments
     larger than 500.

6. Tear down the Flink, Kafka cluster and Prometheus PushGateway after the
   FeatHub program has finished.

   Note that since the FeatHub job is reading from Kafka, it will run
   indefinitely, and you would need to manually press Control-C to stop the
   program.

   ```bash
   docker-compose down
   ```
