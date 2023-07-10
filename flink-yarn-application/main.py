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

from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.file_system_sink import FileSystemSink
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
                "flink": {
                    "deployment_mode": "cli",
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
        path="hdfs:///data/purchase_events.json",
        data_format="json",
        schema=purchase_events_schema,
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S",
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
        path="hdfs:///data/item_price_events.json",
        data_format="json",
        schema=item_price_events_schema,
        keys=["item_id"],
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S",
    )

    # The total cost of purchases made by this user in the last 2 minutes.
    f_total_payment_last_two_minutes = Feature(
        name="total_payment_last_two_minutes",
        transform=OverWindowTransform(
            expr="item_count * price",
            agg_func="SUM",
            window_size=timedelta(minutes=2),
            group_by_keys=["user_id"],
        ),
    )

    purchase_events_with_features = DerivedFeatureView(
        name="purchase_events_with_features",
        source=purchase_events_source,
        features=[
            "item_price_events.price",
            f_total_payment_last_two_minutes,
        ],
        keep_source_fields=True,
    )

    client.build_features(
        [
            item_price_events_source,
            purchase_events_with_features,
        ]
    )

    result_table = client.get_features(purchase_events_with_features)

    result_table_df = result_table.to_pandas()

    print(result_table_df)

    local_sink = FileSystemSink(path="hdfs:///data/output.json", data_format="csv")

    result_table.execute_insert(sink=local_sink, allow_overwrite=True).wait()
