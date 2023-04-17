#  Copyright 2022 The FeatHub Authors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import numpy as np
import pandas as pd
from feathub.common import types
from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.redis_sink import RedisSink
from feathub.feature_tables.sources.file_system_source import FileSystemSource
from feathub.feature_tables.sources.redis_source import RedisSource
from feathub.feature_views.on_demand_feature_view import OnDemandFeatureView
from feathub.table.schema import Schema

if __name__ == "__main__":
    client = FeathubClient(
        props={
            "processor": {
                "type": "flink",
                "flink": {
                    "master": "localhost:8081",
                },
            },
            "online_store": {
                "types": ["memory"],
                "memory": {},
            },
            "registry": {
                "type": "local",
                "local": {
                    "namespace": "default",
                },
            },
            "feature_service": {
                "type": "local",
                "local": {},
            },
        }
    )

    item_price_events_schema = (
        Schema.new_builder()
        .column("item_id", types.String)
        .column("price", types.Float32)
        .column("timestamp", types.String)
        .build()
    )

    item_price_events_source = FileSystemSource(
        name="item_price_events",
        path="/tmp/data/item_price_events.json",
        data_format="json",
        schema=item_price_events_schema,
        keys=["item_id"],
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S %z",
    )

    result_table = client.get_features(item_price_events_source)

    redis_sink = RedisSink(
        host="redis",
    )

    result_table.execute_insert(sink=redis_sink, allow_overwrite=True).wait()

    item_price_features_source = RedisSource(
        name="item_price_features",
        schema=item_price_events_schema,
        keys=["item_id"],
        host="localhost",
        timestamp_field="timestamp",
    )

    on_demand_feature_view = OnDemandFeatureView(
        name="on_demand_feature_view",
        features=[
            "item_price_features.price",
        ],
        request_schema=Schema.new_builder().column("item_id", types.String).build(),
    )
    client.build_features([item_price_features_source, on_demand_feature_view])

    request_df = pd.DataFrame(
        np.array([["item_1"], ["item_2"], ["item_3"]]), columns=["item_id"]
    )

    online_features = client.get_online_features(
        request_df=request_df,
        feature_view=on_demand_feature_view,
    )

    print(online_features)

    expected_features = pd.read_csv("./data/expected_output.csv")
    if not expected_features.equals(online_features):
        raise RuntimeError("Online serving features does not match with expected.")
