import numpy as np
from tqdm import tqdm

from core.database.sqlite3_api import NpArraySupportDatabaseTable

ed = NpArraySupportDatabaseTable(commit_after=10)
ed.connect("data.db")
ed.create_table(
    column_with_types=[("speakerid", "text"), ("utterance", "text"),
                       ("vector", NpArraySupportDatabaseTable.ARRAY_TYPE)],
    drop_if_exists=True)

x = np.arange(12).reshape(2, 6)
ed.insert_table(("a", "b", x))
ed.force_commit()

for i in tqdm(range(1000)):
    for data in ed.select_from_table():
        print(data)