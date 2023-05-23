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

    user_activity_events_schema = (
        Schema.new_builder()
        .column("user_id", types.String)
        .column("item_id", types.String)
        .column("action_type", types.String)
        .column("timestamp", types.Int64)
        .build()
    )

    user_activity_events_source = FileSystemSource(
        name="user_behavior_events",
        path="/tmp/data/user_behavior_events.json",
        data_format="json",
        schema=user_activity_events_schema,
        timestamp_field="timestamp",
        timestamp_format="epoch",
    )

    # TODO: make sure user_id is used as the Kafka message key.
    user_activity_events_sink = KafkaSink(
        bootstrap_server="kafka:9092",
        topic="user_behavior_events",
        key_format=None,
        value_format="json",
    )

    client.materialize_features(
        user_activity_events_source,
        user_activity_events_sink,
        allow_overwrite=True,
    ).wait()
