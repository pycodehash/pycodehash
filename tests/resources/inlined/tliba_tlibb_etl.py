################################################################################
# Module: tliba.random.rng
################################################################################
def draw_beta_samples():
    """Create table consisting of 5000 draws from a Beta(2, 5) distribution."""
    return pd.DataFrame(np.random.beta(2, 5, 5000), columns=["beta"])
################################################################################
# Module: tliba.random
################################################################################
def draw_normal_samples():
    """Create table consisting of 5000 draws from a standard normal distribution."""
    return pd.DataFrame(np.random.normal(0, 1, 5000), columns=["normal"])
################################################################################
# Module: tlibb.etl
################################################################################
def combine_random_samples():
    print("Concat")
    return pd.concat((rng.draw_beta_samples(), normal_samples()), axis=1)
################################################################################
# Module: tliba.random
################################################################################
def draw_bernoulli_samples():
    """Create table consisting of 5000 draws from a bernoulli distribution where the probability is drawn form a Beta(2, 5)."""
    return pd.DataFrame(
        np.random.binomial(1, draw_beta_samples().values.flatten(), 5000),
        columns=["binomial"],
    )
################################################################################
# Module: tlibb.etl
################################################################################
def add_bernoulli_samples():
    print("Hello world")
    df = combine_random_samples().copy()
    df["bernoulli"] = draw_bernoulli_samples()
    return df
