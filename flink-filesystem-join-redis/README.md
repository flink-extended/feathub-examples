# Overview

This example shows how to use `DerivedFeatureView` to enrich the user behavior
event from FileSystem with the item attributes from Redis. It involves the
following steps:

1. Read a stream of user behavior events from a local file.

   Each event has the following fields:
   - user_id, unique identifier of the user.
   - item_id, unique identifier of the item.
   - type, the type of the behavior, e.g., click, exposure.
   - timestamp, time when this behavior is made.

2. Enrich each user activity event by looking up the latest item attributes from
   Redis and joining them onto the events.
   
   Redis could provide attributes with the following fields:
   - item_id, unique identifier of the item.
   - brand, the brand of this item.
   - category, the category of the item.
   - timestamp, time when the item is created or updated.


3. Output the enriched user activity events to a local file.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-filesystem-join-redis`
folder to run this example.

1. Install FeatHub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[flink]"
   ```

2. Start the Flink and the Redis cluster.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink and the Redis clusters have started, you should be able to
   navigate to the web UI at [localhost:8081](http://localhost:8081) to view the
   Flink dashboard.

3. Produce events into the Redis service.

   ```bash
   $ python initialize_redis.py
   ```

4. Run the FeatHub program to compute and output the features to a local file.

   ```bash
   $ python main.py
   ```

   You should be able to see the following messages printed out in your
   terminal.

   ```
   {"user_id":"u6","item_id":"i1","action_type":"exposure","timestamp":1684484065,"brand":"brand1"}
   {"user_id":"u1","item_id":"i9","action_type":"click","timestamp":1684484069,"brand":"brand3"}
   {"user_id":"u10","item_id":"i2","action_type":"exposure","timestamp":1684484066,"brand":"brand1"}
   {"user_id":"u4","item_id":"i4","action_type":"exposure","timestamp":1684484067,"brand":"brand2"}
   {"user_id":"u9","item_id":"i7","action_type":"exposure","timestamp":1684484068,"brand":"brand3"}
   {"user_id":"u9","item_id":"i6","action_type":"exposure","timestamp":1684484068,"brand":"brand2"}
   {"user_id":"u6","item_id":"i5","action_type":"exposure","timestamp":1684484067,"brand":"brand2"}
   {"user_id":"u5","item_id":"i8","action_type":"exposure","timestamp":1684484069,"brand":"brand3"}
   {"user_id":"u3","item_id":"i3","action_type":"exposure","timestamp":1684484066,"brand":"brand1"}
   {"user_id":"u4","item_id":"i10","action_type":"exposure","timestamp":1684484070,"brand":"brand3"}
   ```

5. Tear down the Flink and the Redis clusters after the FeatHub program has
   finished.

   ```bash
   docker-compose down
   ```
