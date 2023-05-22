################################################################################
# Module: tlibb.etl
################################################################################
def combine_random_samples():
    print("Concat")
    return pd.concat((rng.draw_beta_samples(), normal_samples()), axis=1)
################################################################################
# Module: tlibb.etl
################################################################################
def add_bernoulli_samples():
    print("Hello world")
    df = combine_random_samples().copy()
    df["bernoulli"] = draw_bernoulli_samples()
    return df
