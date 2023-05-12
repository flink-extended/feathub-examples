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
from feathub.feature_tables.sinks.hive_sink import HiveSink
from feathub.feature_tables.sources.file_system_source import FileSystemSource
from feathub.feature_tables.sources.hive_source import HiveSource
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

    hive_sink = HiveSink(
        hive_catalog_conf_dir=".",
        database="default",
        table="item_price_events",
        processor_specific_props={
            "sink.partition-commit.watermark-time-zone": "Asia/Shanghai",
            "sink.partition-commit.policy.kind": "metastore,success-file",
        },
    )

    result_table.execute_insert(sink=hive_sink, allow_overwrite=True).wait()

    item_price_features_source = HiveSource(
        name="item_price_events",
        database="default",
        table="item_price_events",
        schema=item_price_events_schema,
        keys=["item_id"],
        hive_catalog_conf_dir=".",
    )

    saved_table = client.get_features(item_price_features_source)

    saved_table_df = saved_table.to_pandas()

    print(saved_table_df)

    local_sink = FileSystemSink(
        path="/tmp/data/output.json",
        data_format="csv",
    )

    result_table.execute_insert(sink=local_sink, allow_overwrite=True).wait()
