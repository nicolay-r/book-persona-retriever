from os import system
from os.path import exists, join

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
for book_id in tqdm(sorted(missed_books)):

    target = join(CEBApi.books_storage_en, f"{book_id}.txt")

    if exists(target):
        continue

    cmd = "wget https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt -O {filename}".format(
        book_id=book_id, filename=target)

    system(cmd)
