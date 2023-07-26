import numpy as np

from core.database.sqlite3_api import NpArraySupportDatabaseTable

ed = NpArraySupportDatabaseTable(commit_after=10)
ed.connect("data.db")
ed.create_table("test", column_with_types=[
    ("speakerid", "text"),
    ("utterance", "text"),
    ("vector", NpArraySupportDatabaseTable.ARRAY_TYPE),
], drop_if_exists=True)

x = np.arange(12).reshape(2, 6)
ed.insert_table(("a", "b", x))
ed.force_commit()

for data in ed.select_from_table():
    print(data)