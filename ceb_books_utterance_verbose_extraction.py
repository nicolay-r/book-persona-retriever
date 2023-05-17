from os.path import realpath, dirname, join

from core.book_dialog import BookDialogueService
from utils_ceb import CEBApi


next_dialog = True
ceb_api = CEBApi()
bs = BookDialogueService()

__current_dir = dirname(realpath(__file__))
with open(join(__current_dir, "./data/filtered/en/dialogs.txt"), "r") as f:

    for l in f.readlines():
        if l.strip() == '~':
            # break within a one dialog
            pass
        elif l == '\n':
            next_dialog = True
            annot = bs.annotate_dialog()
            for a in annot:
                print(book_id, a)
            print()
        elif l != '\n':
            # actual utterance.
            l = l.strip()
            meta, utt = l.split('line:')
            book_id, dialog_region = meta.split('.txt')
            bs.set_book(book_id=book_id)
            # Span of paragraphs.
            l_from, l_to = dialog_region[1:-1].split(":")
            bs.set_paragraphs(l_from=l_from, l_to=l_to)
            bs.register_utterance(utt=utt, l_from=l_from, l_to=l_to)