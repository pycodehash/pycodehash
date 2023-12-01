from pathlib import Path
from statistics import mean, stdev
from timeit import repeat

import pandas as pd
from faker import Faker
from faker.providers import profile

n_records = [1, 10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]


for n in n_records:
    data_file = Path(f"data_{n}.csv")
    if data_file.exists():
        continue

    print("generate data", n)

    Faker.seed(42)
    fake = Faker()
    fake.add_provider(profile)
    df = pd.DataFrame([fake.profile() for _ in range(n)])
    df.to_csv(data_file, index=False)

# Repeat the function this number of times
number = 10
repeats = 3


for n in n_records:
    data_file = Path(f"data_{n}.csv")

    print(f"{n} records, {data_file.stat().st_size} bytes")

    measurements1 = repeat(
        f'hash_file_full("data_{n}.csv")',
        setup="from datasets.local import hash_file_full",
        number=number,
        repeat=repeats,
    )
    measurements2 = repeat(
        f'fh.compute_hash("data_{n}.csv")',
        setup="from datasets.local import LocalFileHash\nfh = LocalFileHash()",
        number=number,
        repeat=repeats,
    )
    print("full hash 8KB reads", mean(measurements1) * 1000, "ms +/-", stdev(measurements1) * 1000, "ms 1x")
    print(
        "approximate hash",
        mean(measurements2) * 1000,
        "ms +/-",
        stdev(measurements2) * 1000,
        "ms",
        round(mean(measurements1) / mean(measurements2)),
        "x",
    )
    print()
