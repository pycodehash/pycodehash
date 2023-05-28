import pandas as pd

import tliba.random.rng as rng
from tliba.random import draw_bernoulli_samples
from tliba.random import draw_normal_samples as normal_samples
from tlibb.constant import nanmax


def combine_random_samples():
    print("Concat")
    return pd.concat((rng.draw_beta_samples(), normal_samples()), axis=1)


def add_bernoulli_samples():
    print("Hello world")
    df = combine_random_samples().copy()
    df["bernoulli"] = draw_bernoulli_samples()
    nanmax(4)
    return df
