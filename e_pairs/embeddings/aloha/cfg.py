class ClusterConfig:
    def __init__(self, acceptable_overlap, perc_cutoff, level1_limit=None, level2_limit=None, weighted=False, log_scale=True):
        assert 3 < perc_cutoff < 50, 'not a good percentage range'
        self.perc_cutoff = perc_cutoff
        self.l1 = level1_limit
        self.l2 = level2_limit
        assert acceptable_overlap > 3, 'acceptable overlap too low'
        self.aco = acceptable_overlap
        self.weighted = weighted
        self.log_scale = log_scale


class MatrixTrainingConfig:
    """Matrix factor training configuration.
       """

    def __init__(self, top_n: int,
                 conf_scale: int, factor: int, regularization: float, iterations: int,
                 random_state=None, safe_pass=None, train_percentage=0.7):
        self.top_n = top_n
        self.conf_scale = conf_scale
        self.factor = factor
        self.regularization = regularization
        self.iterations = iterations
        self.random_state = random_state
        assert 0 < train_percentage < 1
        self.train_percentage = train_percentage
        if safe_pass is not None:
            assert 0 < safe_pass < 1
        self.safe_pass = safe_pass