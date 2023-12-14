import io
import sqlite3
from collections import Counter

import numpy as np


class NpArraySupportDatabaseTable(object):
    """ Wrapper over SQLite3Database that supports
        and provides array type for storing numpy arrays.
        This is a wrapper for a single table!
    """

    ARRAY_TYPE = "array"

    def __init__(self, commit_after=100):
        assert(isinstance(commit_after, int) and commit_after > 0)
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, self.adapt_array)
        # Converts TEXT to np.array when selecting
        sqlite3.register_converter(self.ARRAY_TYPE, self.convert_array)
        self.table_name = "contents"
        self.con = None
        self.table_columns = None
        self.c = Counter()
        self.cur_insert = None
        self.commit_after = commit_after
        self.cur_select = None

    def connect(self, filepath):
        self.con = sqlite3.connect(filepath, detect_types=sqlite3.PARSE_DECLTYPES)

    @staticmethod
    def adapt_array(arr):
        """ http://stackoverflow.com/a/31312102/190597 (SoulNibbler) """
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sqlite3.Binary(out.read())

    @staticmethod
    def convert_array(text):
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)

    def create_table(self, column_with_types, drop_if_exists=False):
        assert(isinstance(column_with_types, list))

        params = ", ".join(["{} {}".format(c, t) for c, t in column_with_types])
        self.table_columns = [c for c, _ in column_with_types]
        cur = self.con.cursor()
        if drop_if_exists:
            cur.execute("drop table if exists {} ".format(self.table_name))
        cur.execute("create table {} ({})".format(self.table_name, params))
        self.con.commit()
        cur.close()

    def insert_table(self, values):
        assert(isinstance(values, tuple))

        # create cursor if it is not exist.
        if self.cur_insert is None:
            self.cur_insert = self.con.cursor()

        # insert information into the datatable.
        self.cur_insert.execute("insert into {name}({columns}) values({values})".format(
            name=self.table_name,
            columns=",".join(self.table_columns),
            values=",".join(["?"] * len(self.table_columns)),
            ), values)

        self.c["rows_inserted"] += 1

        # Do commit operation if necessary.
        if self.c["rows_inserted"] >= self.commit_after:
            self.con.commit()
            self.c["rows_inserted"] = 0

    def select_from_table(self, columns=None, where=None):
        assert(isinstance(columns, list) or columns is None)

        columns = ["*"] if columns is None else columns

        if self.cur_select is None:
            self.cur_select = self.con.cursor()

        return self.cur_select.execute("select {f} from {t}{w}".format(
            f=",".join(columns),
            t=self.table_name,
            # optional where.
            w=" WHERE {}".format(where) if where is not None else ""))

    def force_commit(self):
        self.con.commit()
        self.c["rows_inserted"] = 0

    def close(self):

        for c in [self.cur_select, self.cur_insert]:
            if c is not None:
                c.close()

        self.force_commit()
        self.con.close()


class SQLiteService(object):

    @staticmethod
    def iter_content(target, column_names=None, table="content"):
        print(f"Connecting: {target}")
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            cols = "*" if column_names is None else ",".join(column_names)
            cursor.execute(f"SELECT {cols} FROM {table}")
            for row in cursor:
                yield row
