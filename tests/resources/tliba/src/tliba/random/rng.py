import pandas as pd
import numpy as np


def draw_beta_samples():
    """Create table consisting of 5000 draws from a Beta(2, 5) distribution."""
    return pd.DataFrame(np.random.beta(2, 5, 5000), columns=["beta"])


def draw_normal_samples():
    """Create table consisting of 5000 draws from a standard normal distribution."""
    return pd.DataFrame(np.random.normal(0, 1, 5000), columns=["normal"])


def draw_bernoulli_samples():
    """Create table consisting of 5000 draws from a bernoulli distribution where the probability is drawn form a Beta(2, 5)."""
    return pd.DataFrame(
        np.random.binomial(1, draw_beta_samples().values.flatten(), 5000),
        columns=["binomial"],
    )
