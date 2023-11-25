# Detecting dataset change

A question that we may ask before running expensive computations on a dataset is: has my dataset changed since the last time it was processed?
If the dataset and the computation have not changed, then the output will be the same and the computation can be skipped.

Comparing a dataset with its previous version requires two copies of the data to be stored, which can be costly for larger datasets.
Instead, we can store a [hash](https://en.wikipedia.org/wiki/Hash_function) of the data to avoid this.

## Hashing datasets

Computing the hash value for a dataset, such as a file, scales with the file size. Table 1 shows results on a mock datasets of various sizes:

| Records    | File size | Time     |
|------------|-----------|----------|
| 1          | 402B      | 1.89ms   |
| 10         | 3KB       | 2.92ms*  |
| 100        | 33KB      | 1.94ms   |
| 1.000      | 329KB     | 4.00ms   |
| 10.000     | 3.3MB     | 31.73ms  |
| 100.000    | 32.8MB    | 243.68ms |
| 1.000.000  | 327.6MB   | 2.23s    |
| 10.000.000 | 3.28GB    | 22.23s   |

_Table 1: SHA256 hash of the mock data file. The hash is updated in blocks of 8K. The data is generated with [Faker](https://faker.readthedocs.io/en/master/index.html). The reported time is the mean of 5 trials of 10 repetitions. *Due to the choice for 8KB block reads._

When working with larger datasets, the time needed to compute the hash increases from negligible (<< 1s) to noticeable (couple of seconds).
Note that the time reported is running the hashing 10 times, to be able to measure more accurately.
For larger compute loads that take 1 hour, it might not be a problem to have this overhead if a cache hit means that the job does not need to run.
However, in practice, we still can do better.

## Approximate Hashers

Many datasets do have metadata associated with it that can be used as an alternative to hashing the data itself.
This metadata will remain the same if the data has not changed, and almost certainly changes if modified.
Examples are **Size** and **Modification date** for files.
Retrieving the metadata for a dataset requires constant time. 

| Records             | Full file hashing | Fast approximate hashing | Speedup Ratio |
|---------------------|-------------------|--------------------------|---------------|
| 1 (402B)            | 1.89ms            | 0.17ms                   | 11x           |
| 10 (3KB)            | 2.92ms            | 0.17ms                   | 17x           |
| 100 (33KB)          | 1.94ms            | 0.16ms                   | 12x           |
| 1.000 (329KB)       | 4.00ms            | 0.17ms                   | 23x           |
| 10.000 (3.3MB)      | 31.73ms           | 0.18ms                   | 180x          |
| 100.000 (32.8MB)    | 243.68ms          | 0.19ms                   | 1.313x        |
| 1.000.000 (327.6MB) | 2.23s             | 0.19ms                   | 11.924x       |
| 10.000.000 (3.28GB) | 22.23s            | 0.19ms                   | 114.626x      |

_Table 2: Comparison of sha256 hashing of the full file and fast approximate hashing for various numbers of records. The reported time is the mean of 5 trials of 10 repetitions. The benchmark script can be found in `timing.py`._

In the above table, we can see that the larger the dataset gets the higher speedup ratio is.
To create an `ApproximateHasher` in `pycodehash`, we only need to code the logic to obtain this metadata as a
dictionary in the `collect_metadata` method, and the class does the rest.

## Supported Dataset types

The following approximate hashers are implemented at this time:

- Local files
- Files on S3
- Hive tables

Feel free to open a Pull Request if you would like to contribute additional dataset types. 

## Incremental loads

Many datasets consist of collections of objects, or subsets of data:

- Hive table partitions, e.g. data grouped per day or month
- Directories of images

Hashing these datasets on the object level, allows for only recomputing the parts of the data that have changed.
For these cases, `pycodehash` has the `PartitionedApproximateHasher` base class.
It requires an `ApproximateHasher` and implements the `collect_hashes` method.
Currently, there is an implementation of `LocalDirectoryHash` recursively collects the hashes for each file in that directory.
