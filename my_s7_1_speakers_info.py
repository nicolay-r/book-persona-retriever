from utils_ceb import CEBApi
from utils_my import MyAPI
from utils_pg19 import PG19Api


############################################
# Extract Information about Speakers.
############################################
def get_book_id(v):
    return v.split('_')[0]

ceb_api = CEBApi()
ceb_api.read_char_map()
pg19 = PG19Api()
pg19.read()
roles = ceb_api.get_meta_role()
for s in MyAPI.predefined_speakers:
    book_id = get_book_id(s)
    if int(book_id) in pg19.book_ids():
        title = pg19.find_book_title(book_id)
        print(s, title, ceb_api.get_char_names(s), roles[s] if s in roles else "UNK")


