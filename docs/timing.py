from pathlib import Path
from time import time

import pandas as pd
from datasets.local import LocalFileHash, hash_file_full
from faker import Faker
from faker.providers import profile

n_records = [
    1,
    10,
    100,
    1_000,
    10_000,
    100_000,
    1_000_000,
    10_000_000,
]


for n in n_records:
    data_file = Path(f"data_{n}.csv")
    if data_file.exists():
        continue

    print("generate data", n)

    Faker.seed(42)
    fake = Faker()
    fake.add_provider(profile)
    df = pd.DataFrame(
        [fake.profile() for _ in range(n)],
    )
    df.to_csv(data_file, index=False)

print("timing")
for n in n_records:
    data_file = Path(f"data_{n}.csv")

    print("n", n)
    print("file size", data_file.stat().st_size)

    start = time()
    fh = LocalFileHash()
    fh.compute_hash(data_file)
    end = time()

    print((end - start) * 1000.0, "ms")

    start = time()
    hash_file_full(data_file)
    end = time()
    print((end - start) * 1000.0, "ms")
