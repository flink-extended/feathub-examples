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
   - production_place, the location where the item is produced. It is a map with
     the following entries.
      - country, the country where the item is produced.
      - city, the city where the item is produced.
   
   During the joining, the brand and the city of the production_place would be
   appended to each event. Note that users can use brackets to describe the
   operation to join a static entry in a Map-typed feature, and in this case
   Redis lookup source would only read the specific entry from Redis, instead of
   reading the whole map. 


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
     user_id item_id action_type   timestamp   brand production_city
   0      u6      i1    exposure  1684484065  brand1           cityA
   1     u10      i2    exposure  1684484066  brand1           cityA
   2      u3      i3    exposure  1684484066  brand1           cityB
   3      u4      i4    exposure  1684484067  brand2           cityC
   4      u6      i5    exposure  1684484067  brand2           cityC
   5      u9      i6    exposure  1684484068  brand2           cityC
   6      u9      i7    exposure  1684484068  brand3                
   7      u5      i8    exposure  1684484069  brand3           cityD
   8      u1      i9       click  1684484069  brand3           cityE
   9      u4     i10    exposure  1684484070  brand3           cityF
   ```

5. Tear down the Flink and the Redis clusters after the FeatHub program has
   finished.

   ```bash
   docker-compose down
   ```
