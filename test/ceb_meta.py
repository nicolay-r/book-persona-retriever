from os.path import join

from utils import DATA_DIR
from utils_ceb import CEBApi

# reading char_map
ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
ceb_api.read_char_map()
