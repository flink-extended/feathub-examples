# Overview

This example benchmarks the performance of using FlinkProcessor to execute 
SlidingFeatureView. The SlidingFeatureView consists of multiple SlidingWindowTransform 
of the same step_size, which provides performance optimization opportunities.

# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-sliding-feature-view-benchmark` 
folder to run the benchmarks.

1. Install Feathub pip package.

   ```bash
   $ python -m pip install --upgrade feathub-nightly
   ```

2. Start the Flink cluster.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink cluster has started, you should be able to navigate to the
   web UI at [localhost:8081](http://localhost:8081) to view the Flink dashboard.

3. Run the benchmark to test the performance of the transformations, e.g.

   ```bash
   # The script run the benchmark with total of 10 millions records as input
   $ python main.py
   
   # You can specify the number of records, e.g. 1000
   $ python main.py --records-num 1000
   ```

4. Checkout the outputs.

   You should be able to find the result similar to the following printed out in the 
   end of the terminal.

   ```
   Num records 1000, run time: 0.07 seconds, throughput: 14229 rps
   ```

5. Tear down the Flink cluster after the benchmark has finished.

   ```bash
   docker-compose down
   ```

