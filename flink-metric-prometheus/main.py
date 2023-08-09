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

from datetime import timedelta

from feathub.common import types
from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.black_hole_sink import BlackHoleSink
from feathub.feature_tables.sources.kafka_source import KafkaSource
from feathub.feature_views.derived_feature_view import DerivedFeatureView
from feathub.feature_views.feature import Feature
from feathub.metric_stores.metric import Count, Ratio
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
            "metric_store": {
                "type": "prometheus",
                "report_interval_sec": 5,
                "namespace": "custom_namespace",
                "prometheus": {
                    "server_url": "pushgateway:9091",
                    "delete_on_shutdown": False,
                },
            },
        }
    )

    purchase_events_schema = (
        Schema.new_builder()
        .column("user_id", types.String)
        .column("item_id", types.String)
        .column("price", types.Float32)
        .column("item_count", types.Int32)
        .column("timestamp", types.String)
        .build()
    )

    purchase_events_source = KafkaSource(
        name="purchase_events",
        bootstrap_server="kafka:9092",
        topic="user_behavior_events",
        key_format=None,
        value_format="json",
        schema=purchase_events_schema,
        consumer_group="feathub",
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S",
        startup_mode="earliest-offset",
    )

    f_total_payment = Feature(
        name="total_payment",
        transform="item_count * price",
        metrics=[
            # Compute the number of purchases whose
            # payment is larger than 500 in the last day
            Count(
                filter_expr="> 500",
                window_size=timedelta(days=1),
            ),
            # Compute the proportion of purchases whose
            # payment is larger than 500 so far
            Ratio(filter_expr="> 500"),
        ],
    )

    purchase_events_with_features = DerivedFeatureView(
        name="purchase_events_with_features",
        source=purchase_events_source,
        features=[
            f_total_payment,
        ],
        keep_source_fields=True,
    )

    client.materialize_features(
        feature_descriptor=purchase_events_with_features,
        sink=BlackHoleSink(),
        allow_overwrite=True,
    ).wait()
