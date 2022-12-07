#  Copyright 2022 The Feathub Authors
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

from datetime import timedelta

from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sources.kafka_source import KafkaSource
from feathub.feature_tables.sinks.kafka_sink import KafkaSink
from feathub.feature_views.feature import Feature
from feathub.feature_views.derived_feature_view import DerivedFeatureView
from feathub.feature_views.sliding_feature_view import SlidingFeatureView
from feathub.feature_views.transforms.sliding_window_transform import (
    SlidingWindowTransform,
)

from feathub.common import types
from feathub.table.schema import Schema

if __name__ == "__main__":
    client = FeathubClient(
        props={
            "processor": {
                "type": "flink",
                "flink": {"rest.address": "localhost", "rest.port": 8081},
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

    purchase_events_schema = (
        Schema.new_builder()
        .column("user_id", types.String)
        .column("item_id", types.String)
        .column("item_count", types.Int32)
        .column("timestamp", types.String)
        .build()
    )

    # TODO: update the demo to continuously emit records in the Kafka stream.
    purchase_events_source = KafkaSource(
        name="purchase_events",
        bootstrap_server="kafka:9092",
        topic="purchase_events",
        key_format=None,
        value_format="json",
        schema=purchase_events_schema,
        consumer_group="feathub",
        keys=["user_id"],
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S %z",
        startup_mode="earliest-offset",
    )

    item_price_events_schema = (
        Schema.new_builder()
        .column("item_id", types.String)
        .column("price", types.Float32)
        .column("timestamp", types.String)
        .build()
    )

    item_price_events_source = KafkaSource(
        name="item_price_events",
        bootstrap_server="kafka:9092",
        topic="item_price_events",
        key_format=None,
        value_format="json",
        schema=item_price_events_schema,
        consumer_group="feathub",
        keys=["item_id"],
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S %z",
        startup_mode="earliest-offset",
        is_bounded=True
    )

    purchase_events_with_price = DerivedFeatureView(
        name="purchase_events_with_price",
        source=purchase_events_source,
        features=[
            "item_price_events.price",
        ],
        keep_source_fields=True,
    )

    # The total cost of purchases made by each user in each 2-minute sliding window with
    # 1-minute step size.
    f_total_payment_last_two_minutes = Feature(
        name="total_payment_last_two_minutes",
        dtype=types.Float32,
        transform=SlidingWindowTransform(
            expr="item_count * price",
            agg_func="SUM",
            window_size=timedelta(minutes=2),
            step_size=timedelta(minutes=1),
            group_by_keys=["user_id"],
        ),
    )

    user_online_features = SlidingFeatureView(
        name="user_online_features",
        source=purchase_events_with_price,
        features=[
            f_total_payment_last_two_minutes,
        ],
    )

    client.build_features(
        [
            item_price_events_source,
            user_online_features,
        ]
    )

    user_online_features_sink = KafkaSink(
        bootstrap_server="kafka:9092",
        topic="user_online_features",
        key_format=None,
        value_format="json",
    )

    # TODO: make sure the emitted output is correct.
    result_table = client.get_features(user_online_features)

    result_table_df = result_table.to_pandas(force_bounded=True)

    print(result_table_df)

    job = client.materialize_features(
        user_online_features, user_online_features_sink, allow_overwrite=True
    )
    try:
        job.wait()
    finally:
        job.cancel()
