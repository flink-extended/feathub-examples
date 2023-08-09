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

from feathub.common import types
from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.file_system_sink import FileSystemSink
from feathub.feature_tables.sources.file_system_source import FileSystemSource
from feathub.feature_tables.sources.redis_source import RedisSource
from feathub.feature_views.derived_feature_view import DerivedFeatureView
from feathub.feature_views.feature import Feature
from feathub.feature_views.transforms.join_transform import JoinTransform
from feathub.table.schema import Schema

if __name__ == "__main__":
    client = FeathubClient(
        props={
            "processor": {
                "type": "flink",
                "flink": {
                    "master": "localhost:8081",
                    "native.table.exec.source.idle-timeout": "1000",
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

    user_behavior_events_schema = (
        Schema.new_builder()
        .column("user_id", types.String)
        .column("item_id", types.String)
        .column("action_type", types.String)
        .column("timestamp", types.Int64)
        .build()
    )

    user_behavior_events_source = FileSystemSource(
        name="user_behavior_events",
        path="/tmp/data/user_behavior_events.json",
        data_format="json",
        schema=user_behavior_events_schema,
        timestamp_field="timestamp",
        timestamp_format="epoch",
    )

    item_attributes_schema = (
        Schema.new_builder()
        .column("item_id", types.String)
        .column("brand", types.String)
        .column("category", types.String)
        .column("production_place", types.MapType(types.String, types.String))
        .build()
    )

    item_attributes_source = RedisSource(
        name="item_attributes",
        schema=item_attributes_schema,
        host="redis",
        keys=["item_id"],
    )

    enriched_user_behavior_events = DerivedFeatureView(
        name="enriched_user_behavior_events",
        source=user_behavior_events_source,
        features=[
            "item_attributes.brand",
            Feature(
                name="production_city",
                transform=JoinTransform(
                    table_name="item_attributes",
                    expr="production_place['city']",
                ),
                dtype=types.String,
            ),
        ],
        keep_source_fields=True,
    )

    client.build_features([item_attributes_source, enriched_user_behavior_events])

    result_table = client.get_features(enriched_user_behavior_events)

    result_table_df = result_table.to_pandas()

    print(result_table_df)

    local_sink = FileSystemSink(path="/tmp/data/output.json", data_format="json")

    result_table.execute_insert(sink=local_sink, allow_overwrite=True).wait()
