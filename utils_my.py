from os.path import join, dirname, realpath


class MyAPI:
    """ Dataset developed for this particular studies
    """

    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_annot")

    def __init__(self):
        pass