from os import system

from tqdm import tqdm

from utils_ceb import CEBApi
from utils_pg19 import PG19Api

ceb_api = CEBApi()
ceb_api.read()
ceb_books = ceb_api.book_ids()

pg19_api = PG19Api()
pg19_api.read()
pg19_books = pg19_api.book_ids()
missed_books = ceb_books.difference(pg19_books)

book = "https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8"
for book_id in tqdm(missed_books):

    cmd = "wget https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt -P {p}".format(
        book_id=book_id, p="data/ceb_books")

    system(cmd)
