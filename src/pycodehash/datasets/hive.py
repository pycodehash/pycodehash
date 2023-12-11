from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pyspark

if hasattr(pyspark, "errors"):
    from pyspark.errors.exceptions.captured import AnalysisException
else:
    # pyspark < (3, 4)
    from pyspark.sql.utils import AnalysisException

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

from pycodehash.datasets.approximate_hasher import ApproximateHasher

logger = logging.getLogger(__name__)


class HiveTableHash(ApproximateHasher):
    """Fast approximate hash for spark hive tables"""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        super().__init__()

    def collect_metadata(self, table_name: str) -> dict[str, Any]:
        try:
            data = self.spark.sql(f"DESCRIBE FORMATTED {table_name}").toPandas()
        except AnalysisException:
            logger.error("Could not get table metadata")
            return {}

        # DataFrame logging for debugging
        logger.debug("%s", data)

        if not data[data["col_name"] == "# Partition Information"].empty:
            logger.warning(
                "The Hive table is partitioned. "
                "It is recommended to hash each partition to deal with incremental load."
            )

        # Select relevant columns
        data = data[data["col_name"].isin(["Created Time", "Statistics"])]

        # Convert to dict
        return data.set_index("col_name").to_dict()["data_type"]
