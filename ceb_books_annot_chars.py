from tqdm import tqdm

from utils_ceb import CEBApi
from utils_my import MyAPI

ceb_api = CEBApi()
ceb_api.read_char_map()

found = 0
missed = 0
ceb_api_annot = CEBApi(books_root=MyAPI.books_storage_en)

for book_id in tqdm(ceb_api.book_ids_from_directory(), desc="Annotating characters"):
    with open(ceb_api.get_book_path(book_id)) as f:
        book_text = f.read()
        for char_id in ceb_api.iter_book_chars(book_id):
            # Order characters by placing the long entries first.
            id_and_names = list(enumerate(ceb_api.get_char_names(char_id)))
            char_names = sorted(id_and_names, key=lambda item: len(item[1]), reverse=True)
            for name_id, name in char_names:
                html_annot_name = "{{{char_id}_{var_id}}}".format(char_id=char_id, var_id=name_id)

                if name not in book_text:
                    missed += 1
                else:
                    found += 1

                book_text = book_text.replace(name, html_annot_name)

    ceb_api_annot.save_book(book_id=book_id, text=book_text)

print("Found: {}%".format(round(found/(found+missed) * 100), 4))
print(missed)



