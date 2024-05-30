from collections import Counter


class CounterService:

    @staticmethod
    def from_most_common(ctr, n):
        assert (isinstance(ctr, Counter))
        c = Counter()
        for e, v in ctr.most_common(n):
            c[e] = v
        return c

    @staticmethod
    def to_melt_list(ctr, min_value=None, max_value=None):
        assert (isinstance(ctr, Counter))

        data = []
        for e, count in ctr.items():

            if max_value is not None and max_value < e:
                continue
            if min_value is not None and min_value > e:
                continue

            for _ in range(count):
                data.append(e)

        return data
