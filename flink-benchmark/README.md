# Overview

This folder contains benchmarks to test the performance of the transformations that run
with the Flink processor.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-benchmark` folder to run the 
benchmarks.

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
   $ python multi_size_sliding_feature_view.py
   ```

4. Tear down the Flink cluster after the benchmark has finished.

   ```bash
   docker-compose down
   ```
