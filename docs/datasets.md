# Detecting dataset change

A question that we may ask before running expensive computations on a dataset is: has my dataset changed since the last time it was processed?
If the dataset and the computation have not changed, then the output will be the same and the computation can be skipped.

Comparing a dataset with its previous version requires two copies of the data to be stored, which can be costly for larger datasets.
Instead, we can store a [hash](https://en.wikipedia.org/wiki/Hash_function) of the data to avoid this.

## Hashing datasets

Computing the hash value for a dataset, such as a file, scales with the file size. Table 1 shows results on a mock datasets of various sizes:

| Records    | File size | Time     |
|------------|-----------|----------|
| 1          | 402B      | 0.189ms  |
| 10         | 3KB       | 0.292ms* |
| 100        | 33KB      | 0.194ms  |
| 1.000      | 329KB     | 0.400ms  |
| 10.000     | 3.3MB     | 3.173ms  |
| 100.000    | 32.8MB    | 24.368ms |
| 1.000.000  | 327.6MB   | 0.223s   |
| 10.000.000 | 3.28GB    | 2.223s   |

_Table 1: SHA256 hash of the mock data file. The hash is updated in blocks of 8K. The data is generated with [Faker](https://faker.readthedocs.io/en/master/index.html). The reported time is the mean of 5 trials of 10 repetitions. *Due to the choice for 8KB block reads._

When working with larger datasets, the time needed to compute the hash increases from negligible (<< 1s) to noticeable (couple of seconds).
Note that the time reported is 1/10th of the total time of running the hashing 10 times, to be able to measure more accurately.
For larger compute loads that take 1 hour, it might not be a problem to have this overhead if a cache hit means that the job does not need to run.
However, in practice, we still can do better.

## Approximate Hashers

Many datasets do have metadata associated with it that can be used as an alternative to hashing the data itself.
This metadata will remain the same if the data has not changed, and almost certainly changes if modified.
Examples are **Size**, **Modification date** or [**ETag**](https://en.wikipedia.org/wiki/HTTP_ETag).
The user is responsible for selecting the most collision-resistant subset of metadata depending on the data generation 
process from the available metadata.
Retrieving the metadata for a dataset requires constant time. 

| Records             | Full file hashing | Fast approximate hashing | Speedup Ratio |
|---------------------|-------------------|--------------------------|---------------|
| 1 (402B)            | 0.189ms           | 0.017ms                  | 11x           |
| 10 (3KB)            | 0.292ms           | 0.017ms                  | 17x           |
| 100 (33KB)          | 0.194ms           | 0.016ms                  | 12x           |
| 1.000 (329KB)       | 0.400ms           | 0.017ms                  | 23x           |
| 10.000 (3.3MB)      | 3.173ms           | 0.018ms                  | 180x          |
| 100.000 (32.8MB)    | 24.368ms          | 0.019ms                  | 1.313x        |
| 1.000.000 (327.6MB) | 0.223s            | 0.019ms                  | 11.924x       |
| 10.000.000 (3.28GB) | 2.223s            | 0.019ms                  | 114.626x      |

_Table 2: Comparison of SHA256 hashing of the full file and fast approximate hashing for various numbers of records. The reported time is the mean of 5 trials. Each trial consists of 10 repetitions, for which the average time is listed. The benchmark script can be found in `timing.py`._

In the above table, we can see that the larger the dataset gets, the higher speedup ratio is.
To create an `ApproximateHasher` in `pycodehash`, we only need to code the logic to obtain this metadata as a
dictionary in the `collect_metadata` method, and the class does the rest.
The hash of the metadata is invariant to the ordering of the keys.

## Supported Dataset types

The following approximate hashers are implemented at this time:

| **Dataset Type**                                                                                     | **Implemented Metadata**                |
|------------------------------------------------------------------------------------------------------|-----------------------------------------|
| [Local Files](https://github.com/pycodehash/pycodehash/blob/main/src/pycodehash/datasets/local.py)   | File Size, Modification Date            |
| [Files on S3](https://github.com/pycodehash/pycodehash/blob/main/src/pycodehash/datasets/s3.py)      | ETag                                    |
| [Hive Tables](https://github.com/pycodehash/pycodehash/blob/main/src/pycodehash/datasets/hive.py)    | Size, Creation Date, Is Partitioned     |
| [Python Files](https://github.com/pycodehash/pycodehash/blob/main/src/pycodehash/datasets/python.py) | Magic, Size, Timestamp, Hash, Bit Field |


Feel free to open a Pull Request if you would like to contribute additional dataset types or metadata. 

## Incremental loads

Many datasets consist of collections of objects, or subsets of data:

- Hive table partitions, e.g. data grouped per day or month
- Directories of images

Hashing these datasets on the object level, allows for only recomputing the parts of the data that have changed.
For these cases, `pycodehash` has the `PartitionedApproximateHasher` base class.
It requires an `ApproximateHasher` and implements the `collect_partitions` method.
Currently, there is an implementation of `LocalDirectoryHash` recursively collects the hashes for each file in that directory.
Another implementation of the `PartitionedApproximateHasher` is `LocalFilesHash`, which operates on a list of files.

The `PartitionedApproximateHasher` is an `ApproximateHasher` in itself, which means that the `compute_hash` method is supported.
This hash is invariant to the ordering of the partitions.
