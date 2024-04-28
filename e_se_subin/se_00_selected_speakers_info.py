from os.path import join
from utils import DATA_DIR
from utils_ceb import CEBApi
from utils_pg19 import PG19Api
from utils_se import SEApi


def get_book_id(v):
    return v.split('_')[0]


pg19 = PG19Api()
pg19.read(metadata_path=join(DATA_DIR, "pg19-metadata.txt"))
ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
ceb_api.read_char_map()
for s in SEApi.predefined_speakers:
    book_id = get_book_id(s)
    if int(book_id) in pg19.book_ids():
        title = pg19.find_book_title(book_id)
        print(s, title, ceb_api.get_char_names(s))
