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

from feathub.common import types
from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.file_system_sink import FileSystemSink
from feathub.feature_tables.sources.file_system_source import FileSystemSource
from feathub.feature_views.sql_feature_view import SqlFeatureView
from feathub.table.schema import Schema

if __name__ == "__main__":
    client = FeathubClient(
        props={
            "common": {
                "timeZone": "UTC",
            },
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

    purchase_events_schema = (
        Schema.new_builder()
        .column("user_id", types.String)
        .column("item_id", types.String)
        .column("item_count", types.Int32)
        .column("item_price", types.Float32)
        .column("timestamp", types.String)
        .build()
    )

    purchase_events_source = FileSystemSource(
        name="purchase_events",
        path="/tmp/data/purchase_events.json",
        data_format="json",
        schema=purchase_events_schema,
    )

    purchase_events_with_features_schema = (
        Schema.new_builder()
        .column("user_id", types.String)
        .column("item_id", types.String)
        .column("item_count", types.Int32)
        .column("item_price", types.Float32)
        .column("total_amount", types.Float32)
        .column("timestamp", types.Int64)
        .build()
    )

    purchase_events_with_features = SqlFeatureView(
        name="purchase_events_with_features",
        sql_statement="""
            SELECT 
                LOWER(user_id) AS user_id,
                LOWER(item_id) AS item_id,
                item_count,
                item_price,
                item_count * item_price AS total_amount,
                UNIX_TIMESTAMP(`timestamp`) AS `timestamp`
            FROM purchase_events
            WHERE user_id IS NOT NULL 
                AND REGEXP(LOWER(item_id), '^item_[0-9]+$')
                AND item_count > 0;
        """,
        schema=purchase_events_with_features_schema,
        keys=["item_id"],
    )

    client.build_features(
        [
            purchase_events_source,
            purchase_events_with_features,
        ]
    )

    result_table = client.get_features(purchase_events_with_features)

    result_table_df = result_table.to_pandas()

    print(result_table_df)

    local_sink = FileSystemSink(path="/tmp/data/output.json", data_format="csv")

    result_table.execute_insert(sink=local_sink, allow_overwrite=True).wait()
