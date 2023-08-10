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


from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.kafka_sink import KafkaSink

from feathub.common import types
from feathub.feature_tables.sources.file_system_source import FileSystemSource
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

    browse_events_source = FileSystemSource(
        name="browse_events",
        path="/tmp/data/browse_events.json",
        data_format="json",
        schema=browse_events_schema,
        timestamp_field="timestamp",
        timestamp_format="%Y-%m-%d %H:%M:%S",
    )

    # TODO: make sure user_id is used as the Kafka message key.
    browse_events_sink = KafkaSink(
        bootstrap_server="kafka:9092",
        topic="browse_events",
        key_format=None,
        value_format="json",
    )

    client.materialize_features(
        browse_events_source,
        browse_events_sink,
        allow_overwrite=True,
    ).wait()
