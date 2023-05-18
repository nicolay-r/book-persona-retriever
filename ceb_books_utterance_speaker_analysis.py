from os.path import realpath, dirname, join

from gutenberg_dialog.pipeline.utils import DialogMetaHelper
from nltk import RegexpTokenizer

from core.book_dialog import BookDialogueService
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI

my_api = MyAPI()
bs = BookDialogueService()


def __iter_lines():
    __current_dir = dirname(realpath(__file__))
    with open(join(__current_dir, GuttenbergDialogApi.dialogs_en), "r") as f:

        for l in f.readlines():
            if l.strip() == '~':
                # break within a one dialog
                pass
            elif l == '\n':
                yield book_id, bs.annotate_dialog()
            elif l != '\n':
                # actual utterance.
                l = l.strip()

                args = l.split(DialogMetaHelper._sep)
                if len(args) == 1:
                    continue

                meta, utt = args
                book_id, dialog_region = meta.split('.txt')
                bs.set_book(book_id=book_id, book_path=my_api.get_book_path(book_id))
                # Span of paragraphs.
                l_from, l_to = dialog_region[1:-1].split(":")
                bs.set_paragraphs(l_from=l_from, l_to=l_to)
                bs.register_utterance(utt=utt, l_from=l_from, l_to=l_to)


def __extract(k=None):
    """ analyse the examples in distance from K
    """
    tokenizer = RegexpTokenizer(r'\w+')
    for book_id, lines in __iter_lines():
        filtered = []
        for segment in lines:

            # Collect only author comments.
            if not (segment[0] in ['#', '.']):
                continue

            # Crop metainformation.
            words = segment.split()[1:]

            # Get rid o punctuation.
            segment = ' '.join(tokenizer.tokenize(segment))

            # Select k.
            if k is not None:
                if k < len(words) and words[k][0] == '{':
                    ok = True
                else:
                    ok = False
            else:
                ok = True

            # Collect utterance.
            if ok:
                filtered.append(segment)

        if len(filtered) > 0:
            yield book_id, filtered


books_count = my_api.books_count()
print(books_count)

# Collect.
for k in [None] + list(range(20)):
    book_dialogs = {}
    for book_id, lines in __extract(k):
        if book_id not in book_dialogs:
            book_dialogs[book_id] = []
        book_dialogs[book_id].append(lines)

    books_total = len(book_dialogs)
    avg = sum([len(book_dialogs) for book_dialogs in book_dialogs.values()]) / books_count
    print("At least one segment in dialog mention author at position {k} (avg/book): ".format(k=k), round(avg, 2),
          "[{} of {}]".format(books_total, books_count))