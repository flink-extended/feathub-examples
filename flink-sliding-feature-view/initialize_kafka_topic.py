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
from feathub.feature_tables.sinks.file_system_sink import FileSystemSink
from feathub.feature_tables.sinks.kafka_sink import KafkaSink
from feathub.feature_views.feature import Feature
from feathub.feature_views.derived_feature_view import DerivedFeatureView
from feathub.feature_views.transforms.over_window_transform import (
    OverWindowTransform,
)

from feathub.common import types
from feathub.feature_tables.sources.file_system_source import FileSystemSource
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

    purchase_events_source = FileSystemSource(
        name="purchase_events",
        path="/tmp/data/purchase_events.json",
        data_format="json",
        schema=purchase_events_schema,
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S",
    )

    # TODO: make sure user_id is used as the Kafka message key.
    purchase_events_sink = KafkaSink(
        bootstrap_server="kafka:9092",
        topic="purchase_events",
        key_format=None,
        value_format="json",
    )

    client.materialize_features(
        purchase_events_source,
        purchase_events_sink,
        allow_overwrite=True,
    ).wait()

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
        timestamp_format="%Y-%m-%d %H:%M:%S",
    )

    # TODO: make sure item_id is used as the Kafka message key.
    item_price_events_sink = KafkaSink(
        bootstrap_server="kafka:9092",
        topic="item_price_events",
        key_format=None,
        value_format="json",
    )

    client.materialize_features(
        item_price_events_source,
        item_price_events_sink,
        allow_overwrite=True,
    ).wait()
