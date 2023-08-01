from os.path import realpath, dirname, join

from gutenberg_dialog.pipeline.utils import DialogMetaHelper

from core.book.book_dialog import BookDialogue
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI

next_dialog = True
my_api = MyAPI()
bs = BookDialogue()

__current_dir = dirname(realpath(__file__))
with open(join(__current_dir, GuttenbergDialogApi.dialogs_en), "r") as f:

    for l in f.readlines():
        if l.strip() == '~':
            # break within a one dialog
            pass
        elif l == '\n':
            next_dialog = True
            annot = bs.annotate_dialog()
            print_sep = False
            for a in annot:
                if a[0] in ['!', "#", '.', ">"]:
                    print(book_id, a)
                    print_sep = True

            if print_sep:
                print()
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
