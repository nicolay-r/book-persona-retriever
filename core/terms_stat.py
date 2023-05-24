import math


class TermsStat:

    def __init__(self):
        self.__terms_total = {}
        self.__terms_in_doc = {}
        self.__doc_ids = set()

    def iter_terms(self):
        return self.__terms_total.keys()

    def docs_count(self):
        return len(self.__doc_ids)

    def get_term_in_docs_count(self, term):
        return self.__terms_in_doc[term]

    def register_doc(self, doc_id, terms):

        # Check whether document has been added already.
        if doc_id in self.__doc_ids:
            return

        self.__doc_ids.add(doc_id)

        used = set()
        for term in terms:

            # Register in total.
            if term not in self.__terms_total:
                self.__terms_total[term] = 1
            else:
                self.__terms_total[term] += 1

            # Register in doc-related.
            if term in used:
                continue
            used.add(term)

            if term not in self.__terms_in_doc:
                self.__terms_in_doc[term] = 1
            else:
                self.__terms_in_doc[term] += 1

    def tfa_idf(self, term, p_threshold=None):
        """ sum(tf,d){1..d} - idf
        """
        assert((isinstance(p_threshold, float) and p_threshold < 1.0) or p_threshold is None)

        p_threshold = 0.0 if p_threshold is None else p_threshold

        t_count = self.__terms_total[term]
        tfa = t_count * 1.0 / sum(self.__terms_total.values())

        # Calculate the threshold in percentage.
        mn = min(self.__terms_total.values())
        mx = max(self.__terms_total.values())
        threshold = mn + (mx - mn) * p_threshold

        # Filtering.
        if p_threshold is not None and t_count < threshold:
            return 0

        idf = math.log(len(self.__doc_ids) * 1.0 / self.__terms_in_doc[term])
        return tfa * idf

    def df(self, term):
        return self.__terms_in_doc[term]
