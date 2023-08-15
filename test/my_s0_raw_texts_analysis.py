from utils_ceb import CEBApi

# reading char_map
ceb_api = CEBApi()
ceb_api.read_char_map()

book_ids = ceb_api.book_ids_from_directory()
books_count = len(book_ids)
chars_count = ceb_api.characters_count(book_ids=book_ids)

print("Books Considered: {}".format(books_count))
print("Characters Count: {}".format(chars_count))
print("Characters per book: {}".format(round(chars_count / books_count, 2)))

print(ceb_api.get_meta_gender())
print(ceb_api.get_meta_role())
