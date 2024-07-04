def range_middle(n):
    return [round(n / 2)]


def range_exclude_middle(n):
    middle = range_middle(n)[0]
    return [i for i in range(n) if i != middle]
