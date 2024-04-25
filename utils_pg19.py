from os.path import realpath, dirname, join

import pandas as pd


class PG19Api:
    """ Books from Project Gutenberg for 19th Century.
    """

    def __init__(self):
        self.__pg19_titles = None

    def read(self, metadata_path):
        self.__pg19_titles = pd.read_csv(metadata_path, header=None)
        self.__pg19_titles.columns = ["id", "title", "year", "link"]

    def find_book_title(self, book_id):
        assert(isinstance(book_id, str))
        assert(self.__pg19_titles is not None)
        series = self.__pg19_titles[self.__pg19_titles["id"] == int(book_id)]["title"]
        return series.iloc[0] if len(series) > 0 else None

    def book_ids(self):
        return set(self.__pg19_titles["id"].to_list())
