import pytest

try:
    from pycodehash.datasets.hive import HiveTableHash
    from pyspark.sql import SparkSession

    spark_found = True
except (ModuleNotFoundError, AttributeError):
    spark_found = False


@pytest.fixture(scope="function")
def spark():
    return SparkSession.builder.appName("spark-test").enableHiveSupport().getOrCreate()


@pytest.fixture(scope="function")
def employee_dataset(spark, tmp_path):
    table_name = "employee"
    employee = spark.sparkContext.parallelize(
        [
            (1, "James", 30, "M"),
            (2, "Ann", 40, "F"),
            (3, "Jeff", 41, "M"),
            (4, "Jennifer", 20, "F"),
            (5, "Noone", -1, "X"),
        ]
    ).toDF(["id", "name", "age", "gender"])
    employee.write.mode("overwrite").option("path", str(tmp_path)).saveAsTable(table_name)
    return employee, tmp_path, table_name


@pytest.mark.skipif(not spark_found, reason="spark not found - install spark")
def test_approximate_hasher_hive(spark, employee_dataset):
    employee_df, tmp_path, table_name = employee_dataset

    hasher = HiveTableHash(spark)
    initial_metadata = hasher.collect_metadata(table_name)
    assert isinstance(initial_metadata, dict)
    assert initial_metadata["Statistics"] == "6449 bytes"

    initial_hash = hasher.compute_hash(table_name)
    assert isinstance(initial_hash, str)

    # Access
    spark.table(table_name).show(n=5, truncate=False)

    second_hash = hasher.compute_hash(table_name)
    assert initial_hash == second_hash

    # Append
    employee_df.union(employee_df).write.mode("overwrite").option("path", str(tmp_path)).saveAsTable(table_name)

    third_hash = hasher.compute_hash(table_name)
    assert initial_hash != third_hash
    third_metadata = hasher.collect_metadata(table_name)
    assert third_metadata["Statistics"] == "12361 bytes"
