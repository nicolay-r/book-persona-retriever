import json


class CBEApi:

    def __init__(self):
        self.__book_by_char = None
        self.__chars = None

    def read(self, path="./data/charembench/data/chr_map.json"):
        """ reading char_map
        """
        self.__book_by_char = {}
        with open(path, "r") as f:
            self.__chars = json.load(f)
            for char_id in self.__chars.keys():
                book_id = char_id.split('_')[0]
                self.__book_by_char[char_id] = book_id

    def get_char_name(self, char_id):
        return self.__chars[char_id][0]
