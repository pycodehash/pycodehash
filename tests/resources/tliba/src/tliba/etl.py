import pandas as pd

import tliba.random.rng as rng
from tliba.random import draw_bernoulli_samples
from tliba.random import draw_normal_samples as normal_samples


def combine_random_samples():
    return pd.concat((rng.draw_beta_samples(), normal_samples()), axis=1)


def add_bernoulli_samples():
    df = combine_random_samples().copy()
    df["bernoulli"] = draw_bernoulli_samples()
    return df
