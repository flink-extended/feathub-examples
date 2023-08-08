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
from feathub.feature_tables.sources.kafka_source import KafkaSource
from feathub.feature_tables.sources.redis_source import RedisSource
from feathub.feature_views.derived_feature_view import DerivedFeatureView
from feathub.feature_views.feature import Feature
from feathub.feature_views.on_demand_feature_view import OnDemandFeatureView
from feathub.feature_views.transforms.over_window_transform import OverWindowTransform
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

    browse_events_schema = (
        Schema.new_builder()
        .column("user_id", types.Int32)
        .column("item_id", types.Int64)
        .column("event_type", types.String)
        .column("timestamp", types.String)
        .build()
    )

    browse_events_source = KafkaSource(
        name="browse_events",
        bootstrap_server="kafka:9092",
        topic="browse_events",
        key_format=None,
        value_format="json",
        schema=browse_events_schema,
        consumer_group="feathub",
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S",
        startup_mode="earliest-offset",
        is_bounded=True,
    )

    # The last ten clicked items of this user.
    f_last_10_click_history = Feature(
        name="click_history",
        transform=OverWindowTransform(
            expr="item_id",
            agg_func="COLLECT_LIST",
            limit=10,
            group_by_keys=["user_id"],
            filter_expr="event_type = 'click'",
        ),
    )

    browse_events_with_features = DerivedFeatureView(
        name="browse_events_with_features",
        source=browse_events_source,
        features=[
            f_last_10_click_history,
        ],
        filter_expr="click_history IS NOT NULL",
    )

    client.build_features([browse_events_with_features])

    result_table = client.get_features(browse_events_with_features)

    redis_sink = RedisSink(
        host="redis",
        keep_timestamp_field=False,
    )

    result_table.execute_insert(sink=redis_sink, allow_overwrite=True).wait()

    click_history_schema = (
        Schema.new_builder()
        .column("user_id", types.Int32)
        .column("click_history", types.VectorType(types.Int64))
        .build()
    )

    click_history_source = RedisSource(
        name="click_history_source",
        schema=click_history_schema,
        keys=["user_id"],
        host="localhost",
    )

    on_demand_feature_view = OnDemandFeatureView(
        name="on_demand_feature_view",
        features=[
            "click_history_source.click_history",
        ],
        request_schema=Schema.new_builder().column("user_id", types.String).build(),
    )
    client.build_features([click_history_source, on_demand_feature_view])

    request_df = pd.DataFrame(np.array([[1], [2], [3]]), columns=["user_id"])

    online_features = client.get_online_features(
        request_df=request_df,
        feature_view=on_demand_feature_view,
    )

    print(online_features)

    online_features.to_csv("./data/output.csv", index=False)
