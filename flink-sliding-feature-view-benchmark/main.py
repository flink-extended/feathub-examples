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
import argparse
import sys
import time
from datetime import timedelta

from feathub.common import types
from feathub.common.types import Int64
from feathub.feathub_client import FeathubClient
from feathub.feature_tables.sinks.black_hole_sink import BlackHoleSink
from feathub.feature_tables.sources.datagen_source import DataGenSource, RandomField
from feathub.feature_views.feature import Feature
from feathub.feature_views.sliding_feature_view import SlidingFeatureView
from feathub.feature_views.transforms.sliding_window_transform import (
    SlidingWindowTransform,
)
from feathub.table.schema import Schema


def run(records_num: int):
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
        .column("user_id", types.Int32)
        .column("item_id", types.Int32)
        .column("item_count", types.Int32)
        .column("timestamp", types.Timestamp)
        .build()
    )
    purchase_events_source = DataGenSource(
        name="purchase_events",
        schema=purchase_events_schema,
        number_of_rows=records_num,
        rows_per_second=sys.maxsize,
        field_configs={
            "user_id": RandomField(minimum=0, maximum=9),
            "item_id": RandomField(minimum=0, maximum=9),
            "item_count": RandomField(minimum=1, maximum=4),
        },
        keys=["user_id"],
        timestamp_field="timestamp",
    )
    step_size = timedelta(milliseconds=2)
    user_purchase_cnt_features = SlidingFeatureView(
        name="user_purchase_cnt_features",
        source=purchase_events_source,
        features=[
            Feature(
                name="total_purchase_2_ms",
                transform=SlidingWindowTransform(
                    expr="item_count",
                    agg_func="SUM",
                    window_size=timedelta(milliseconds=2),
                    step_size=step_size,
                    group_by_keys=["user_id"],
                ),
            ),
            Feature(
                name="total_purchase_5_ms",
                transform=SlidingWindowTransform(
                    expr="item_count",
                    agg_func="SUM",
                    window_size=timedelta(milliseconds=5),
                    step_size=step_size,
                    group_by_keys=["user_id"],
                ),
            ),
            Feature(
                name="total_purchase_10_ms",
                transform=SlidingWindowTransform(
                    expr="item_count",
                    agg_func="SUM",
                    window_size=timedelta(milliseconds=10),
                    step_size=step_size,
                    group_by_keys=["user_id"],
                ),
            ),
            Feature(
                name="total_purchase_100_ms",
                transform=SlidingWindowTransform(
                    expr="item_count",
                    agg_func="SUM",
                    window_size=timedelta(milliseconds=100),
                    step_size=step_size,
                    group_by_keys=["user_id"],
                ),
            ),
            Feature(
                name="total_purchase_10_s",
                transform=SlidingWindowTransform(
                    expr="item_count",
                    agg_func="SUM",
                    window_size=timedelta(seconds=10),
                    step_size=step_size,
                    group_by_keys=["user_id"],
                ),
            ),
        ],
    )
    job = client.materialize_features(
        features=user_purchase_cnt_features, sink=BlackHoleSink(), allow_overwrite=True
    )
    try:
        start_time = time.time()
        job.wait()
        run_time = time.time() - start_time
        print(
            f"Num records {records_num}, run time: {run_time:.2f} seconds, "
            f"throughput: {int(records_num / run_time)} rps"
        )
    finally:
        job.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--records-num", type=int, default=10_000_000)
    args = parser.parse_args()
    run(args.records_num)
