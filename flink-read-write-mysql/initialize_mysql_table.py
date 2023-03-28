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
import time
from typing import Optional

import mysql.connector


def wait_for_mysql_server(
    host: str, user: str, password: str, timeout_sec: float = 60.0
) -> None:
    """
    Wait for the MySQL server to start by attempting to connect to it until the
    connection is successful or the timeout is reached.
    """
    start_time = time.time()
    while True:
        try:
            print("Waiting for MySQL Server...")
            mysql.connector.connect(host=host, user=user, password=password)
            break
        except mysql.connector.Error:
            if time.time() - start_time > timeout_sec:
                raise TimeoutError("Failed to wait for MySQL Server.")
            time.sleep(5)

    print("MySQL Server is up and running.")


def execute_sql(
    host: str, user: str, password: str, sql: str, database: Optional[str] = None
) -> None:
    """
    Execute an SQL command on a MySQL server.
    """
    with mysql.connector.connect(
        host=host, user=user, password=password, database=database
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


wait_for_mysql_server(host="localhost", user="root", password="root")

execute_sql(
    host="localhost",
    user="root",
    password="root",
    sql="CREATE DATABASE IF NOT EXISTS feathub",
)

execute_sql(
    host="localhost",
    user="root",
    password="root",
    database="feathub",
    sql="CREATE TABLE IF NOT EXISTS item_price_features ("
    "`item_id` VARCHAR(64) PRIMARY KEY, "
    "`price` DOUBLE, "
    "`timestamp` VARCHAR(64))",
)
