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
from feathub.feature_tables.sinks.redis_sink import RedisSink
from feathub.feature_tables.sources.file_system_source import FileSystemSource
from feathub.feature_views.derived_feature_view import DerivedFeatureView
from feathub.feature_views.feature import Feature
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

    item_attributes_schema = (
        Schema.new_builder()
        .column("item_id", types.String)
        .column("brand", types.String)
        .column("category", types.String)
        .column("production_country", types.String)
        .column("production_city", types.String)
        .build()
    )

    item_attributes_source = FileSystemSource(
        name="item_attributes",
        path="/tmp/data/item_attributes.csv",
        data_format="csv",
        schema=item_attributes_schema,
        timestamp_field=None,
        keys=["item_id"],
    )

    item_attributes_view = DerivedFeatureView(
        name="item_attributes_view",
        source=item_attributes_source,
        features=[
            "item_id",
            "brand",
            "category",
            Feature(
                name="production_place",
                transform="MAP('country', production_country, 'city', production_city)",
            ),
        ],
        keep_source_fields=False,
    )

    result_table = client.get_features(item_attributes_view)

    redis_sink = RedisSink(
        host="redis",
    )

    result_table.execute_insert(sink=redis_sink, allow_overwrite=True).wait()
