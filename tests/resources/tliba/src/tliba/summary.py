import numpy as np

from tliba.etl import combine_random_samples
from tliba.etl import add_bernoulli_samples


def compute_moments():
    return combine_random_samples().aggregate([np.mean, np.median, "var"])


def compute_conditional_moments():
    df = add_bernoulli_samples()
    return df.groupby("bernoulli").aggregate([np.mean, np.median, "var"])
