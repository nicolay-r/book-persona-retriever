import logging

import implicit
import numpy as np
from implicit.evaluation import train_test_split, precision_at_k
from scipy.sparse import coo_matrix

logger = logging.getLogger('example_logger')


class MatrixWrapper:

    def to_coo(self, data):
        user_cat = data[self.col1].astype('category')
        feature_cat = data[self.col2].astype('category')
        coo = coo_matrix((data[self.col3], (user_cat.cat.codes.copy(), feature_cat.cat.codes.copy())))
        return coo, user_cat, feature_cat

    def __init__(self, df, user_col, feature_col, value_col):
        assert len(df) > 0
        self.col1 = user_col
        self.col2 = feature_col
        self.col3 = value_col

        # build coo for col1, 2
        self.coo, self.cat1, self.cat2 = self.to_coo(df)
        logger.info(repr(self.coo))
        self.model = None

        # build category mapping data
        # m1 is for object, m2 is for feature
        # maps is built from both directions: forward direction cat_id: value.
        self.m1 = dict(enumerate(self.cat1.cat.categories))
        self.m1_inv = {r: i for i, r in self.m1.items()}
        self.m2 = dict(enumerate(self.cat2.cat.categories))
        self.m2_inv = {r: i for i, r in self.m2.items()}
        self.m1_count = len(self.m1)
        self.m2_count = len(self.m2)
        # all key and value should be unique (map to category id)
        assert self.m1_count == len(self.m1_inv)
        assert self.m2_count == len(self.m2_inv)

    def get_train(self, train_config, report_test=True, test_df=None, overwrite=False):
        if self.model and not overwrite:
            raise Exception('Already trained and does not allow overwrite (consider access via model instance).')

        assert train_config, 'train configuration has to be provided.'

        if report_test:
            logger.info('-- Performing MM sanity check on {} {}'.format(self.col1, self.col2))
            if test_df is None:
                if train_config.random_state:
                    np.random.seed(train_config.random_state)
                train_csr, test_csr = train_test_split(self.coo, train_percentage=train_config.train_percentage)
            else:
                assert len(test_df) > 0
                train_csr = self.coo
                test_csr, _, _ = self.to_coo(test_df)
            _model = implicit.als.AlternatingLeastSquares(factors=train_config.factor,
                                                          regularization=train_config.regularization,
                                                          iterations=train_config.iterations)
            _model.fit(train_csr * train_config.conf_scale)
            prec = precision_at_k(_model, train_csr, test_csr, K=train_config.top_n)
            logger.warning('ACCURACY REPORT at top {}: {:.5f}'.format(train_config.top_n, prec))
            if train_config.safe_pass:
                assert prec > train_config.safe_pass

        # training on complete matrix
        logger.info('Training on complete matrix')
        _model = implicit.als.AlternatingLeastSquares(factors=train_config.factor,
                                                      regularization=train_config.regularization,
                                                      iterations=train_config.iterations)
        _model.fit(self.coo * train_config.conf_scale)
        self.model = _model

    def convert(self, value, to_category=True, feature=False, raising=True):
        _map = None
        if to_category:  # id -> category
            if feature:  # get feature
                _map = self.m2_inv
            else:
                _map = self.m1_inv
        else:  # category -> id
            if feature:
                _map = self.m2
            else:
                _map = self.m1
        # get value
        try:
            res = _map[round(value, 6)]
        except KeyError:
            if raising:
                logger.warn('DEBUG MAP: {}'.format(_map))
                raise KeyError('Map does not exists for value: {}'.format(value))
            else:
                return None
        return res

    def get_similar_user(self, id_, top_n=None, convert_back=True):
        if not self.model:
            raise Exception('Model has not been trained yet (call get_train first)')
        cat = self.convert(id_, feature=False, to_category=True, raising=False)
        if cat is not None:
            res = self.model.similar_users(cat, N=top_n)
            if convert_back:
                return [(self.convert(e[0], to_category=False, feature=False), e[1]) for e in np.column_stack(res)]
            return res
        else:  # possibly the entry is filtered out due to low feature count.
            return []
