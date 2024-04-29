from os.path import join

from api.ceb import CEBApi
from utils import DATA_DIR

# reading char_map
ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
ceb_api.read_char_map()
