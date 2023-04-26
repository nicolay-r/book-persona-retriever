import pandas as pd


class PG19Api:

    def __init__(self):
        self.__pg19_titles = None

    def read(self, path):
        self.__pg19_titles = pd.read_csv(path, header=None)
        self.__pg19_titles.columns = ["id", "title", "year", "link"]

    def find_book_title(self, book_id):
        series = self.__pg19_titles[self.__pg19_titles["id"] == int(book_id)]["title"]
        return series.iloc[0] if len(series) > 0 else None
